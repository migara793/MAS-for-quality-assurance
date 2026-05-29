const calculator = require('../math.js');

describe('Calculator', () => {
  test('adds 1 + 2 to equal 3', () => {
    expect(calculator.add(1, 2)).toBe(3);
  });

  test('subtracts 2 - 1 to equal 1', () => {
    expect(calculator.subtract(2, 1)).toBe(1);
  });

  test('multiplies 2 * 3 to equal 6 (BUGGED, SHOULD BE 6)', () => {
    expect(calculator.multiply(2, 3)).toBe(6); // Fixed bug
  });

  test('divides 6 / 2 to equal 3', () => {
    expect(calculator.divide(6, 2)).toBe(3);
  });

  test('divides by zero throws error', () => {
    expect(() => calculator.divide(5, 0)).toThrow('Division by zero is not allowed.');
  });

  test('calculates 2^3 to equal 8', () => {
    expect(calculator.power(2, 3)).toBe(8);
  });

  test('absolute value of -5 is 5', () => {
    expect(calculator.absolute(-5)).toBe(5);
  });
});
