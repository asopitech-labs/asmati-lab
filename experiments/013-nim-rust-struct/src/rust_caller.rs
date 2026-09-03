use std::ffi::c_int;
use std::mem::{align_of, offset_of, size_of};

#[repr(C)]
#[derive(Clone, Copy)]
struct AsmatiPair {
    left: c_int,
    right: c_int,
}

unsafe extern "C" {
    fn asmati_add(left: c_int, right: c_int) -> c_int;
    fn asmati_sum_pair(pair: AsmatiPair) -> c_int;
}

const _: () = {
    assert!(size_of::<c_int>() == 4);
    assert!(size_of::<AsmatiPair>() == 8);
    assert!(align_of::<AsmatiPair>() == 4);
    assert!(offset_of!(AsmatiPair, left) == 0);
    assert!(offset_of!(AsmatiPair, right) == 4);
};

fn main() {
    println!(
        "size={} align={} left={} right={}",
        size_of::<AsmatiPair>(),
        align_of::<AsmatiPair>(),
        offset_of!(AsmatiPair, left),
        offset_of!(AsmatiPair, right)
    );
    for (index, (left, right, expected)) in [(19, 23, 42), (-100, 7, -93), (32767, 1, 32768)]
        .into_iter()
        .enumerate()
    {
        let pair = AsmatiPair { left, right };
        // The declarations match the generated C header, all fields are initialized,
        // and these inputs fit C int. No pointer or ownership is transferred.
        // The POSIX library constructor initializes Nim before main executes.
        let (scalar, aggregate) = unsafe { (asmati_add(left, right), asmati_sum_pair(pair)) };
        assert_eq!(scalar, expected);
        assert_eq!(aggregate, expected);
        println!("case={index} scalar={scalar} pair={aggregate}");
    }
}
