type
  Animal = ref object of RootObj
    id: int
  Dog = ref object of Animal
    bonus: int

proc staticScore(animal: Animal): int {.noinline.} =
  animal.id + 100

method dynamicScore(animal: Animal): int {.base, noinline.} =
  animal.id + 100

method dynamicScore(dog: Dog): int {.noinline.} =
  dog.id + dog.bonus

proc callStatic(animal: Animal): int {.noinline.} =
  staticScore(animal)

proc callDynamic(animal: Animal): int {.noinline.} =
  dynamicScore(animal)

let animal: Animal = Dog(id: 5, bonus: 7)

echo "static=", callStatic(animal)
echo "dynamic=", callDynamic(animal)
