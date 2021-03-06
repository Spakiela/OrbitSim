import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from scipy.integrate import odeint, solve_ivp
from scipy.optimize import newton
from matplotlib.widgets import Slider, TextBox
import matplotlib.gridspec as gridspec
import seaborn as sb
from numba import vectorize

# GUI updates: Solve recursion problem to add slider for periapsis, autoscale effective potential plot, dont allow
# objects to move outside of the plot, add user optimization to only allow excepted values for sliders, add text boxes
# for angular momentum and periapsis values, add some way to change simulation run time.

# GUI items needing to be added: Gravitational wave plots, Resonance heat map, gravitational radiation

# GUI wishlist for future updates: Add some way to enable and disable gravitational radiation. Display resonant energy
# on effective potential graph

# Calculate number of whirls

# Start Time
t_i = 0
# End Time
t_f = 50000
# Step Interval = h
Step = 1
# Mass of massive body
M = 1
# Gravitational Constant
G = 1
# Angular Momentum
L = 4
# Energy
E = 0
# Array Size
size = (t_f - t_i)/Step
size = int(size)
# Time Array
Time = np.arange(t_i, t_f, Step)
# Initial radius
r_i = 5.244
# Initial radial velocity
rdot_i = 0
# Initial Phi
phi_i = 0


# Creating the effective potential function
r = sp.Symbol('r')
U_Eff = (-G*M/r + L**2/(2*r**2) - G*M*(L**2)/r**3)
U_Eff_Func = sp.lambdify(r, U_Eff)
Eff_Force = -sp.diff(U_Eff, r)
Eff_Force_Func = sp.lambdify(r, Eff_Force)
Phi_dot = L/r**2
Phi_dot_Func = sp.lambdify(r, Phi_dot)


# Plotting Effective Potential
x = np.linspace(1, 20, 1000)
y = np.zeros_like(x)
for i in range(y.size):
    y[i] = U_Eff_Func(x[i])


# Creating a line to represent particles energy
def energy_line(Radius):
    y1 = np.zeros_like(x)
    for i in range(x.size):
        y1[i] = U_Eff_Func(Radius)
    return y1


def root1(r):
    return E + G*M/r - L**2/(2*r**2) + G*M*(L**2)/r**3 - (1/2) * rdot_i**2


def root2(r):
    return sp.diff(U_Eff, r)


# Integration method for solve_ivp
def deriv(t, y):
    return [y[1], Eff_Force_Func(y[0]), Phi_dot_Func(y[0])]


# event tracking method to track apoapsis
def apoapsis(t, y):
    return y[1]


apoapsis.terminal = False
apoapsis.direction = -1


# Array of initial conditions
y0 = [r_i, rdot_i, phi_i]
# Array of solutions
sol = solve_ivp(deriv, y0=y0, t_span=[t_i, t_f], t_eval=Time, rtol=1e-8, atol=1e-8, events=apoapsis)


# Creates Plotting window
fig1 = plt.figure(num='Orbit Applet', figsize=(16, 9))
plt.subplots_adjust(bottom=.25)
spec1 = gridspec.GridSpec(ncols=2, nrows=1, figure=fig1)
# Plotting orbit
ax1 = fig1.add_subplot(spec1[0, 0], projection='polar')
ax1.set_title('Orbit')
orbit, = plt.polar(sol.y[2], sol.y[0])
plt.ylim(0, 25)
# Plotting Effective Potential
ax2 = fig1.add_subplot(spec1[0, 1])
ax2.set_title('Effective Potential')
a1, = plt.plot(x, y)
plt.ylim(-.2, .2)
# Adds periapsis on Effective Potential
a2, = plt.plot(r_i, U_Eff_Func(r_i), "or")
# Adds Energy Line on Effective Potential
a3, = plt.plot(x, energy_line(r_i), "--b", alpha=.3)
# Displays current Energy
ax2.text(r_i+.02, U_Eff_Func(r_i)+.02, 'Energy=' + str(int(U_Eff_Func(r_i)*(10**5))/(10**5)))
# Add slider for energy
ax_E = plt.axes([.15, .15, .5, .02], facecolor='lightgoldenrodyellow')
s_E = Slider(ax_E, 'Energy', -.05, .05, valinit=U_Eff_Func(r_i), valstep=.00001)
# Add slider for angular momentum
ax_L = plt.axes([.15, .1, .5, .02], facecolor='lightgoldenrodyellow')
s_L = Slider(ax_L, 'Ang Momentum', 0, 10, valinit=L, valstep=.01)
# Add slider for periapse
ax_R = plt.axes([.15, .05, .5, .02], facecolor='lightgoldenrodyellow')
s_R = Slider(ax_R, 'Periapsis', 0, 10, valinit=r_i, valstep=.001)

# Add text box to manually input initial radius
ax_text = plt.axes([.75, .15, .1, .03])
text_bot = TextBox(ax_text, ' ', initial=str(int(U_Eff_Func(r_i) * (10 ** 5)) / (10 ** 5)))


# Function to zoom in and out of orbit plot w/ scroll wheel
def zoom(ax, scale):
    def zoom_event(event):
        cur_ylim = ax.get_ylim()
        if event.button == 'up':
            scale_fac = 1/scale
        elif event.button == 'down':
            scale_fac = scale
        else:
            scale_fac = 1
        ax.set_ylim([0, cur_ylim[1]*scale_fac])
        plt.draw()

    fig = ax.get_figure()
    fig.canvas.mpl_connect('scroll_event', zoom_event)

    return zoom_event


f = zoom(ax1, 1.5)


# Function to update plots when energy is changed
def update_e(val):
    global E
    E = s_E.val
    global r_i
    r_i = newton(root1, x0=4, maxiter=200, x1=10)
    s_R.set_val(r_i)
    global y0
    y0 = [r_i, rdot_i, phi_i]
    temp_sol = solve_ivp(deriv, y0=y0, t_span=[t_i, t_f], t_eval=Time, rtol=1e-8, atol=1e-8)
    orbit.set_data(temp_sol.y[2], temp_sol.y[0])
    a2.set_data(r_i, U_Eff_Func(r_i))
    a3.set_data(x, energy_line(r_i))
    del ax2.texts[-1]
    ax2.text(r_i + .02, U_Eff_Func(r_i) + .02, 'Energy=' + str(int(U_Eff_Func(r_i) * (10 ** 5)) / (10 ** 5)))
    text_bot.set_val(int(E * 10 ** 5) / 10 ** 5)
    fig1.canvas.draw_idle()


# Function to change angular momentum
def update_l(val):
    global L
    L = s_L.val
    global E
    E = s_E.val
    global r_i
    r_i = newton(root1, x0=4, maxiter=200, x1=10)
    global U_Eff
    U_Eff = (-G * M / r + L ** 2 / (2 * r ** 2) - G * M * (L ** 2) / r ** 3)
    global U_Eff_Func
    U_Eff_Func = sp.lambdify(r, U_Eff)
    global Eff_Force
    Eff_Force = -sp.diff(U_Eff, r)
    global Eff_Force_Func
    Eff_Force_Func = sp.lambdify(r, Eff_Force)
    global Phi_dot
    Phi_dot = L / r ** 2
    global Phi_dot_Func
    Phi_dot_Func = sp.lambdify(r, Phi_dot)
    global y0
    y0 = [r_i, rdot_i, phi_i]
    temp_sol = solve_ivp(deriv, y0=y0, t_span=[t_i, t_f], t_eval=Time, rtol=1e-8, atol=1e-8)
    orbit.set_data(temp_sol.y[2], temp_sol.y[0])
    y = np.zeros_like(x)
    for i in range(y.size):
        y[i] = U_Eff_Func(x[i])
    a1.set_data(x, y)
    a2.set_data(r_i, U_Eff_Func(r_i))
    a3.set_data(x, energy_line(r_i))
    del ax2.texts[-1]
    ax2.text(r_i + .02, U_Eff_Func(r_i) + .02, 'Energy=' + str(int(E * (10 ** 5)) / (10 ** 5)))
    fig1.canvas.draw_idle()


# Function to update periapsis
def update_r(val):
    global r_i
    r_i = s_R.val
    global y0
    y0 = [r_i, rdot_i, phi_i]
    global E
    E = U_Eff_Func(r_i)
    s_E.set_val(E)
    text_bot.set_val(E)
    temp_sol = solve_ivp(deriv, y0=y0, t_span=[t_i, t_f], t_eval=Time, rtol=1e-8, atol=1e-8)
    orbit.set_data(temp_sol.y[2], temp_sol.y[0])
    a2.set_data(r_i, U_Eff_Func(r_i))
    a3.set_data(x, energy_line(r_i))
    fig1.canvas.draw_idle()


# Function to update Energy from text box
def submit(text):
    s_E.set_val(eval(text))
    update_e(text)


# calls updating functions for sliders and text box
s_E.on_changed(update_e)
s_L.on_changed(update_l)
# s_R.on_changed(update_r)
text_bot.on_submit(submit)


print((2*np.pi) % ((sol.y_events[0][0][2] - sol.y_events[0][1][2]) % (2*np.pi)))


def resonance():
    energy_array = np.arange(start=-0.037, stop=-0.002, step=.00001)
    resonance_value = np.zeros_like(energy_array)
    for i in range(energy_array.size):
        global E
        E = energy_array[i]
        global r_i
        r_i = newton(root1, x0=4, maxiter=200, x1=10)
        s_R.set_val(r_i)
        global y0
        y0 = [r_i, rdot_i, phi_i]
        temp_sol = solve_ivp(deriv, y0=y0, t_span=[t_i, t_f], t_eval=Time, rtol=1e-8, atol=1e-8, events=apoapsis)
        resonance_value[i] = (2*np.pi) % ((temp_sol.y_events[0][0][2] - temp_sol.y_events[0][1][2]) % (2*np.pi))
        print(i)
    plt.figure(num='resonance test')
    plt.plot(energy_array[:], resonance_value[:])


# resonance()


plt.show()
