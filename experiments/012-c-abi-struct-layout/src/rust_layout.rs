use std::mem::{align_of, offset_of, size_of};

#[repr(C)]
struct AsmatiLayout {
    first: i32,
    second: i32,
    ratio: f32,
}

const _: () = assert!(size_of::<AsmatiLayout>() == 12);
const _: () = assert!(align_of::<AsmatiLayout>() == 4);
const _: () = assert!(offset_of!(AsmatiLayout, first) == 0);
const _: () = assert!(offset_of!(AsmatiLayout, second) == 4);
const _: () = assert!(offset_of!(AsmatiLayout, ratio) == 8);

fn main() {
    println!(
        "rust size={} align={} first={} second={} ratio={}",
        size_of::<AsmatiLayout>(),
        align_of::<AsmatiLayout>(),
        offset_of!(AsmatiLayout, first),
        offset_of!(AsmatiLayout, second),
        offset_of!(AsmatiLayout, ratio),
    );
}
