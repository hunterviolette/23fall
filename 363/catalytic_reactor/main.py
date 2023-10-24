import sympy as sp

# Define the symbols and the function
v_, rho, t = sp.symbols('v_ rho t')
f = v_ * rho / t

# Calculate partial derivatives
df_dv = sp.diff(f, v_)
df_drho = sp.diff(f, rho)
df_dt = sp.diff(f, t)

# Define specific values for the symbols
v_value = 5.0
rho_value = 2.0
t_value = 1.0

# Substitute the values into the partial derivative functions
df_dv_value = df_dv.subs({v_: v_value, rho: rho_value, t: t_value})
df_drho_value = df_drho.subs({v_: v_value, rho: rho_value, t: t_value})
df_dt_value = df_dt.subs({v_: v_value, rho: rho_value, t: t_value})

# Display the results
print("Partial derivative with respect to v_ at v=5, rho=2, t=1:", df_dv_value)
print("Partial derivative with respect to rho at v=5, rho=2, t=1:", df_drho_value)
print("Partial derivative with respect to t at v=5, rho=2, t=1:", df_dt_value)
