type
  Animal = ref object of RootObj
    id: int
  Dog = ref object of Animal
    barkVolume: int
  Cat = ref object of Animal
    lives: int

proc identify(animal: Animal): int {.noinline.} =
  if animal of Dog:
    Dog(animal).barkVolume
  elif animal of Cat:
    -Cat(animal).lives
  else:
    0

proc forceDog(animal: Animal): int {.noinline.} =
  Dog(animal).barkVolume

when defined(forceFailedCast):
  let dog: Animal = Dog(id: 1, barkVolume: 7)
  let cat: Animal = Cat(id: 2, lives: 9)
  echo "checkedDog=", identify(dog)
  echo "forced=", forceDog(cat)
else:
  let dog: Animal = Dog(id: 1, barkVolume: 7)
  let cat: Animal = Cat(id: 2, lives: 9)
  echo "dogOfDog=", dog of Dog
  echo "catOfDog=", cat of Dog
  echo "dogResult=", identify(dog)
  echo "catResult=", identify(cat)
  echo "forcedDog=", forceDog(dog)
