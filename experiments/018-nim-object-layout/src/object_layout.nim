type
  Sample = object
    count: int
    enabled: bool
    ratio: float

proc score(sample: Sample): float {.noinline.} =
  if sample.enabled:
    float(sample.count) * sample.ratio
  else:
    0.0

static:
  doAssert sizeof(Sample) == 24
  doAssert alignof(Sample) == 8
  doAssert offsetOf(Sample, count) == 0
  doAssert offsetOf(Sample, enabled) == 8
  doAssert offsetOf(Sample, ratio) == 16

let sample = Sample(count: 6, enabled: true, ratio: 1.5)
echo "size=", sizeof(Sample), " align=", alignof(Sample)
echo "fieldSizes int=", sizeof(int), " bool=", sizeof(bool),
  " float=", sizeof(float)
echo "count=", offsetOf(Sample, count),
  " enabled=", offsetOf(Sample, enabled),
  " ratio=", offsetOf(Sample, ratio)
echo "score=", score(sample)
