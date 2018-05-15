# Encoding Streams Explained
14 May 2018

## What’s all this then?

**TextDecoderStream** is used to convert a stream of text in a binary encoding to a
[stream](https://streams.spec.whatwg.org/) of strings.

**TextEncoderStream** is used to convert a stream of strings into bytes in the UTF-8 encoding.

Both APIs satisfy the concept of a
[transform stream](https://streams.spec.whatwg.org/#ts-model). They are the streaming equivalents of
TextDecoder and TextEncoder.

### Goals

The goal is to provide a ubiquitous, correct implementation of a common primitive. Everyone who uses
[streaming
fetch()](https://developer.mozilla.org/en-US/docs/Web/API/Streams_API/Using_readable_streams#Consuming_a_fetch_as_a_stream)
with text will need this functionality. Ad hoc implementations frequently corrupt data when a
character is split between chunks. It is also important to correctly handle
[backpressure](https://streams.spec.whatwg.org/#backpressure) to avoid buffering all the input data
in memory.

Providing this primitive as part of the platform allows user agents to apply optimisations that are
not possible for user-supplied implementations. Since the internals are not visible to Javascript,
the Javascript engine can be bypassed altogether. Sophisticated optimisations such as thread
offloading also become possible.

### Non-goals

* Output encodings other than UTF-8. TextEncoder doesn't support them either. See [Security
  background](https://encoding.spec.whatwg.org/#security-background). For input, every
  encoding in the [Encoding Standard](https://encoding.spec.whatwg.org/#names-and-labels)
  is supported.
* Unification of WHATWG Streams with the concept of a
  [stream](https://encoding.spec.whatwg.org/#concept-stream) used in the Encoding Standard. Despite
  having the same name, they are different in functionality and purpose. Since the Encoding
  Standard's "stream" concept is just an internal piece of spec terminology, this has no impact on
  developers.
* Support for bring-your-own-buffer encoding is not an immediate goal. This is expected to be
  included in a future evolution of the API.

## Getting started / example code

The most common usage pattern will be to decode binary data retrieved from a fetch(). By default the
binary data will be interpreted as UTF-8.

```javascript
const response = await fetch(url);
const bodyAsTextStream = response.body.pipeThrough(new TextDecoderStream());
```

## Key scenarios

### Scenario 1

TextEncoderStream can be used in a similar way to upload a stream of text:

```javascript
const body = textStream.pipeThrough(new TextEncoderStream());
fetch('/dest', { method: 'POST', body, headers: {'Content-Type': 'text/plain; charset=UTF-8'} });
```


### Scenario 2

Streaming new text into a page is a popular use-case for streams. Here is one approach which
creates a new span for each chunk and appends it an element.

```javascript
async function appendURLToElement(url, element) {
  const appendStream = new WritableStream({
    write(chunk) {
      const span = document.createElement('span');
      span.textContent = chunk;
      element.appendChild(span);
    }
  });
  const response = await fetch(url);
  response.body.pipeThrough(new TextDecoderStream())
    .pipeTo(appendStream);
}
```

There are a number of different approaches possible: see https://streams.spec.whatwg.org/demos/ for
examples of streaming structured data or html into a page.

## Detailed design discussion

### Handling of split surrogate pairs

The existing TextEncoder `encode()` method does not have support for split surrogate pairs. However,
when splitting text into chunks using `substring()` it is easy for split surrogate pairs to
occur. It would lead to data corruption issues that would be hard to track down. For this reason,
TextEncoderStream will reassemble surrogate pairs that are split between chunks. Other unmatched
surrogates will still be replaced with unicode replacement characters so that the output is always
valid UTF-8.

## Considered alternatives
* A static method called `TextDecoder.stream()` could have been used. However, returning a plain
  TransformStream from this method would have meant that the accessors providing information about
  the encoding and settings in use would not have been available. Since that was unacceptable, the
  method would have had to return an object like TextDecoderStream. At that point, it makes more
  sense to just expose the TextDecoderStream constructor directly.
* Adding `readable` and `writable` properties directly to TextEncoder and TextDecoder objects is an
  attractive alternative. However, the interaction of the transform stream interface with the
  existing method interface was difficult to specify, and no solution that would satisy everyone
  could be found.

## Appendix A: How Not To Do It

### Example 1: appendURLToElement

Taking the appendURLToElement example above, here's a common approach that doesn't use
TextDecoderStream.

```javascript
async function appendURLToElement(url, element) {
  const appendStream = new WritableStream({
    write(chunk) {
      const chunkAsText = new TextDecoder().decode(chunk);
      const span = document.createElement('span');
      span.textContent = chunkAsText;
      element.appendChild(span);
    }
  });
  const response = await fetch(url);
  response.body.pipeTo(appendStream);
```

This isn't difficult, but is wrong. It works as long as the input is all ASCII, but will fail as
soon as a non-ASCII character is split on a chunk boundary.

It's possible to fix it using the [`stream` option to
`decode()`](https://encoding.spec.whatwg.org/#dom-textdecodeoptions-stream):

```javascript
async function appendURLToElement(url, element) {
  const decoder = new TextDecoder();
  const appendStream = new WritableStream({
    write(chunk) {
      const chunkAsText = decoder.decode(chunk, {stream: true});
      const span = document.createElement('span');
      span.textContent = chunkAsText;
      element.appendChild(span);
    },
    close() {
      const remaining = decoder.decode();
      if (remaining !== '') {
        const span = document.createElement('span');
        span.textContent = chunkAsText;
        element.appendChild(span);
      }
    }
  });
  const response = await fetch(url);
  response.body.pipeTo(appendStream);
```

We had to add a `close()` method to the underlying sink to clean up if the input ends with an
incomplete character. This is now correct, but longer and harder to understand.

### Example 2: fetchAsTextStream

A common approach is to try to wrap the ReadableStream in the Fetch Response in another
ReadableStream.

```javascript
function fetchAsTextStream(url, encoding) {
  return new ReadableStream({
    async start(controller) {
      const response = await fetch(url);
      const decoder = new TextDecoder(encoding);
      const reader = response.body.getReader();
      while (true) {
        const {value, done} = await reader.read();
        if (done) {
          // Flush any buffered characters.
          controller.enqueue(decoder.decode());
          return;
        }
        const stringValue = decoder.decode(value, {stream: true});
        controller.enqueue(stringValue);
      }
    }
  });
}
```

As well as being verbose, this breaks backpressure: data will accumulate in memory as quickly as the
network supplies it, regardless of whether the browser can process it that quickly or not.

TextDecoderStream makes this concise and preserves backpressure:

```javascript
async function fetchAsTextStream(url, encoding) {
  const response = await fetch(url);
  return response.body.pipeThrough(new TextDecoderStream(encoding));
}
```

## References & acknowledgements

Many thanks to Anne van Kesteren, Domenic Denicola, Henri Sivonen, Jake Archibald, Joshua Bell,
Takeshi Yoshino, and Yutaka Hirano for input, design advice and support.
