import sympy as sp

x = sp.symbols('x')
integral = sp.integrate(x**3 * sp.sqrt(x**2 + 1), x)
print(integral)
