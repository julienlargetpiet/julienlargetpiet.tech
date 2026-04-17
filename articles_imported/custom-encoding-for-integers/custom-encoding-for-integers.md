Ok, so i had to encode a structured data, a positive integer in this case representing the space for the server to reserve a byte slice for a file content, image, text...

Basically, how to convert any **positive integer to a vector of number that accepts value from 0 to 255**.

# Encoding

First solution, i just add 256, which will be 255 (from 0) in a vector, and the ending position value will be the rest of the integer minus the previous additions. But that is non optimal, because the vector is too long.

Something that reduces more the size of the integer is of course a division, which will reduce a lot the size of the sending byte vector.

Ok, so this is it for encoding:

```go

func IntToByteSlice(x int) []byte {
  if x == 256 {
    return []byte{0, 0}
  } else if x < 256 {
    return []byte{byte(x)}
  }
  var rtn_byte []byte
  var rest int = x % 256
  rtn_byte = append(rtn_byte, byte(rest))
  x -= rest
  x /= 256
  for x > 256 {
    rtn_byte = append(rtn_byte, 255)
    rest = x % 256
    rtn_byte = append(rtn_byte, byte(rest))
    x -= rest
    x /= 256
  }
  rtn_byte = append(rtn_byte, byte(x - 1))
  return rtn_byte
}

```

# Decoding

and this algorithm for decoding:

```go

func ByteSliceToInt(x []byte) int {
  var rtn_int int = 256
  var ref_mult int = 256
  var i int = len(x) - 1
  if i == 0 {
    return int(x[0])
  }
  for i > -1 {
    rtn_int = ((int(x[i]) + 1) * ref_mult + int(x[i - 1]))
    ref_mult = rtn_int
    i -= 2
  }
  return rtn_int
}

```

# Explanation

In the first algorithm, we take the integer, make sure that it is divisible by 256.

If not already we substract the necessary and put it in the first position of the byte slice, divides the integer, put the result in the second position, take the result and so on until it reaches below 256.
So the vector has \\\*always a length equal to a multiple of 2.

Always is not really exact, because if the integer is less than 256, i can just put it in a 1 size byte slice.

By this process wa are sure that every value of the byte slice is between 0 and 255.

In the second algorithm, we start from the end, multiply by 256 the last value, add the associated rest and take this value that we will multiply with the `n - 3` value (n being the length of the slice/vector), add the rest which is at `n - 4` and so on...