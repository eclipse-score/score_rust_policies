#![deny(clippy::panic)]
#![deny(clippy::unwrap_used)]
#![deny(clippy::expect_used)]
#![deny(clippy::todo)]
#![deny(clippy::unimplemented)]
#![deny(clippy::dbg_macro)]
#![deny(clippy::print_stdout)]
#![deny(clippy::print_stderr)]

/// Adds two numbers without panicking on overflow.
#[must_use]
pub fn saturating_add(a: u32, b: u32) -> u32 {
    a.saturating_add(b)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn adds_without_overflowing() {
        assert_eq!(saturating_add(u32::MAX - 1, 2), u32::MAX);
    }
}
