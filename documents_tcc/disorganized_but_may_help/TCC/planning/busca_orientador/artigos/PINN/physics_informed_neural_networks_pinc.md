1. Introduction
Physics-Informed Neural Networks (PINNs) ( Raissi et al. , 2019) have
been widely used to solve Partial Dierential Equations (PDEs) and Ordi-
nary Dierential Equations (ODEs), representing an alternative to numerical
methods that can speed up simulation orders of magnitude. Once trained,
these networks can output directly the solution without access to the PDE
or ODE equations. Actually, these equations are employed only during the
training phase by designing a loss function that considers a measure of the
deviation of the derivative of the network’s output from the physics laws
given by ODEs/PDEs. In this way, the PINN is trained so that its output
satises the constraints of the physics, in addition to the traditional data
loss for regression,i.e., the mean squared error of the data points. Regard-
ing an ODE or PDE, this data loss corresponds to the error concerning the
initial or boundary conditions. For industrial plants represented by ODEs,
one could collect more data points in addition to initial conditions to com-
plement dierential equations with uncertain or unknown parameters ( Raissi
et al. , 2019).
Applications of PINNs are widespread in many engineering areas. Ouyang
et al. (2023) employed multiple serial PINNs to decouple the governing
physics equations for learning the reconstruction of hydrofoil cavitationow.
Nazari et al. (2023) successfully applied PINNs for modeling river channels
and parameter discovery under conditions of limited system measurements
and Wu et al. (2022) employed PINNs foruidow generation. Many exten-
sions of PINNs exist. For instance, Dwivedi and Srinivasan (2020) extended
Extreme Learning Machines as physics-informed networks for rapidly learn-
ing solutions to PDEs; Xiang et al. (2022) introduced an improved PINN
with a self-adaptive loss function to dynamically weigh the loss terms relat-
ing to data and physics; Tang et al. (2023) devised a parallel physics-informed
neural network to solve the multi-body dynamic equations in full-scale train
collision simulation, while Zhou et al. (2022) developed a physics-informed
generative adversarial network-based approach to facilitate uncertainty quan-
tication and propagation in addition to enabling measurement data fusion
into system reliability assessment.
PINNs have been extended for long-range simulation and control applica-
tions in Antonelo et al. (2024), as they cannot inherently cope with changing
inputs or extrapolate the predictions for time periods longer than the one
dened during training. To address these limitations, Antonelo et al. (2024)
2+
presented a new framework called Physics-Informed Neural Nets for Control
(PINC), which is a novel PINN-based architecture suitable for control prob-
lems and able to simulate for longer-range time horizons that are notxed
beforehand during training. As a result, PINC is moreexible than tradi-
tional PINNs and faster than numerical methods as it relies only on signal
propagation through the network, making it less computationally costly and
better suited for model simulation in Model Predictive Control, for instance.
Model Predictive Control (MPC) is a widely applied method for multivariate
control in both industry and academia ( Camacho and Bordons , 2013), which
has been used successfully in variouselds such as oil and gas ( Jordanou
et al. , 2022), aerospace ( Eren et al. , 2017), process industries, and robotics
(Nascimento et al. , 2018) since its inception in the 1970s.
The class of systems that Antonelo et al. (2024) showed PINC to be ef-
fective include the Van der Pol oscillator and the four-tank system. Despite
being benchmark systems for nonlinear dynamics, their dynamic equations
are smooth functions that may lack specic characteristics of real-world com-
plex systems. These particular features, such as nonsmoothness, may hinder
the training of PINC networks. Here, we investigate improved versions of
the PINC framework for a class of systems that exhibit highly complex and
nonsmooth behavior. In particular, we are interested in modeling and control
of gas-lifted oil wells, which are discussed in Section 3. The baseline version
of PINC as originally proposed did not succeed in modeling and controlling
the oil wells considered in this paper. The three main reasons for that are:
1) the magnitude of the gradient of the physics-loss function was too low for
training to progress consistently; 2) some ODE equations of the well model
include functions not dened for negative numbers; 3) and highly nonlin-
ear or nonsmooth terms of the ODE functions can negatively inuence the
training of the PINC.
For such systems, nonsmoothness impairs the learning eciency as some
terms in the ODE and, consequently, in the PINN’s loss function, lack a
continuous derivative at specic points within its domain, exemplied when
the left-hand and right-hand derivatives at a point are unequal or do not
exist ( Clarke, 1990). This property captures abrupt changes in the function’s
behavior, such as jumps or kinks that arise in the oil well model through the
maximum operator.
The complexity of the class of systems we consider is related not only to
their nonsmothness, but also to: 1) thesizeof the model in terms of the
number of variables and constraints in the DAE/ODE, namely the oil well
3+
model has 3 state equations and 34 algebraic equations, which is far more
complex than the applications in Antonelo et al. (2021) with only either two
or four states, without algebraic equations and variables; 2) the nonlinear
mappings between the variables, e.g., fractional exponents, ratios, and max-
imum operators; 3) functions in the ODE that are not dened for negative
numbers, e.g., square root and logarithm. The more these occur, arguably
the more complex the system is, increasing the occurrence of failure modes in
PINNs ( Fuks and Tchelepi , 2020; Raissi, 2018; Wang et al. , 2022). Besides,
some of these systems may exhibit stiness due to the interaction of multiple
physical processes that operate at dierent time scales.
The contributions of this work are discussed next. Therst issue pre-
sented above was mainly tackled by using skip connections as in Wang et al.
(2021), aiming to improve the magnitude of the gradient through the PINN’s
layers. In that work, they showed that traditional PINNs have specic gra-
dient pathologies, which can be dealt with by the novel architecture and a
learning rate annealing algorithm. In the current work, we transfer their
proposed novel PINN architecture with skip connections to the PINC frame-
work, showing that this improvement was essential for the modeling and
controlling more complex systems such as the oil well. The remaining issues,
which refer to the terms in the ODE equations, are dealt with by modifying
these equations when they appear in the physics-loss function for training
the PINC. This is to say that surrogate terms can replace specic terms to
render training smoother and more ecient. Notice that the latter procedure
is specic to the application at hand,i.e., the oil well model. Lastly, we pro-
pose a hierarchical architecture with two modules: therst one corresponds
to a PINC trained to predict the states of the oil well; and the second one is
a standard feedforward neural network (NN) trained to predict the algebraic
variables of the system (e.g., bottom-hole pressure) based on the predictions
of the states by the PINC (rst module),i.e., the output of the PINC is
the input to the second NN. This NN streamlines the training of additional
algebraic variables without retraining the PINC, which would be far more
computationally costly than just training an NN.
The remainder of this work is organized as follows. Section 2 discusses
some works from the literature related to applying the PINC framework in
model predictive control. Section 3 introduces gas-lifting in oil wells and
presents the dierential algebraic equations that model the process. The
PINN and PINC frameworks, along with the proposed improvements to the
PINC, evaluation metrics, and MPC, are presented in Section 4. In the
4+
following section, the experimental setup is described, while in Section 6, the
results are showcased. Section 7 concludes this work.
2. Related Works
Nicodemus et al. (2022) used the PINC framework, without skip connec-
tions (unlike our work), for model predictive control of multi-body dynamics.
The results show that the PINC framework eectively solves a tracking prob-
lem for a complex mechanical system, a multi-link manipulator. Applying
to a PowerCube serial robot, they demonstrate that the simulation of the
nonlinear dynamics with PINC speeds up the computation time relative to
numerical methods while retaining sucient accuracy.
Liu and Wang (2021) proposed a model-based Reinforcement Learning
(RL) algorithm that utilizes physical laws to learn the state transition dynam-
ics of an agent’s environment. The algorithm employs an encoder-decoder
recurrent network architecture to model the state transition function by min-
imizing the violation of conservation laws. The learned transition model is
then employed to generate samples for an alternative replay buer, which
improves sample eciency in the RL update process and reduces the need
for real-world interactions. However, this approach diers from our PINC-
based approach. Liu and Wang (2021) build the physics-loss function on the
discretized form of the laws of the system, unlike our work that relies on the
continuous form. While they use recurrent networks, our approach employs
feedforward networks in which time is explicitly given as input.
Gokhale et al. (2022) applied a PINN approach to learning a control-
oriented thermal model of a building. The authors assume that the model is
a discrete-time transition function in a Markov Decision Process (MDP) that
predicts the next state, given the current state and action. This approach
allows for control actions to be input to the model. However, unlike in our
approach, their physics loss function also needs to be discretized. Although
their proposal is control-oriented, they do not demonstrate actual control ex-
periments with the trained PINNs, unlike the results from our work presented
in Section 6.
3. Gas-lifted Oil Wells
Primary recovery is therst stage of extracting oil and gas from reser-
voirs. It relies on the natural dierence in pressure between the surface and
5+
the underground reservoir, therefore requiring relatively limited capital in-
vestment. With the gradual extraction of oil from the well, the pressure
underground will slowly decrease, causing the volume of oil production to
decline. Secondary recovery techniques are employed to mitigate the pres-
sure loss, such as water injection, which seeks to force oil to the surface by
directly applying pressure. Also, articial lifting techniques are applied in
wells, particularly those found in deep-water oshore reservoirs, to increase
the pressure gradient from the bottom hole to the surface. A widely used
technique for articial lifting is gas-lift. It works by injecting high-pressure
gas at the bottom of the well, reducing the density of the production stream
and forcing theow ofuids to the surface. Gas-lift is a favored technique for
its desirable features, which include low installation and maintenance cost,
robustness, and a wide range of operating conditions.
The dynamic model for gas-lifted oil wells considered here is a system
of Dierential Algebraic Equations (DAE) developed by Jahanshahi et al.
(2012). The derivation of the model simplied some algebraic equations to
avoid implicit terms, resulting in an explicit model. Consequently, the DAE
system can be regarded as a system of Ordinary Dierential Equations (ODE)
and simulated using, for instance, the Runge-Kutta method. These simpli-
cations are imposed on the equations for velocities and will be explained
further in the text.
3.1. Well Model
The model has several variables, several of which are similar in nature
(pressures and densities, e.g.) but for dierent well locations. Subscript ab-
breviations are used extensively in the variables to refer to the phase (gas
or liquid) and location. The notation is presented in Table 1. An impor-
tant remark is that this model does not distinguish between water and oil,
considering only a liquid phase.
3.1.1. States
The system state is characterized by the mass of gas in the annulusm G,an,
mass of gas in the tubingm G,tb, and mass of liquid in the tubingm L,tb. The
dierential equations are:
˙mG,an =w G,in −w G,inj (1a)
˙mG,tb =w G,inj +w G,res −w G,out (1b)
˙mL,tb =w L,res −w L,out (1c)
6+
Figure 1: Schematics of a gas-lifted oil well ( Jahanshahi et al. , 2012). Liquid and gas from
the reservoir enter the well at the bottom of the tubing, referred to as the bottom hole.
From there, the gas and liquidow up through the tubing until they exit through the
production choke. The tubing is encased by a larger tube called the annulus. At the top
of the annulus, gas is injected through the gas-lift choke. This gasows down the annulus
and enters the production tubing through a check valve (directional/one-way valve) near
the annulus’s bottom. This gas helps “lift” the reservoirow up the tubing, increasing
the production of the well. This kind of articial lift is commonly used when the pressure
in the reservoir is insucient to sustain theow from the reservoir to the top side.
where:w G,in is the gas massow injected into the top of the annulus through
the gas-lift choke;w G,inj is the gas massow from the annulus into the tubing
through the injection check valve, located close to the bottom of the well;
wG,res andw L,res are the gas and liquid massows from the reservoir into the
tubing;w G,out andw L,out are the gas and liquid massows out of the well
through the production choke, or simply the gas and liquid production of the
well.
The equations that calculate theows appearing in state equations as
well as the parameters for three oil well models used in the experiments are
introduced in Appendix A . Refer to Jahanshahi et al. (2012) for a full account
7+
Table 1: Abbreviations used in the subscript of the model variables indicate the phase and
location the respective variable represents.
Abbreviation Description
Ggas
Lliquid
anannulus
tbtubing
bhbottom-hole
ttop
bbottom
of the model. The parameters appearing in the equations are explained in
Table A.4.
4. Methods
4.1. Physics-Informed Neural Networks (PINN)
Physics-Informed Neural Networks (PINNs) ( Raissi et al. , 2019) are trained
to reproduce the solution of a dynamic system by utilizing the known (or par-
tially known) underlying physics of the system. The use of physics knowledge
greatly reduces the need for training data, in some cases removing it com-
pletely. Here, the output of the PINN represents the solution of an ODE.
Let us consider the Initial Value Problem (IVP):
˙y=f(y),y(0) =y 0 (2)
where we are interested in obtaining the solutiony(t) on some intervalt∈
[0, T]. For somef(y), the IVP can be solved analytically, while for others,
obtaining an analytic solution is not possible or practical, in which case
we have the choice of using numerical methods,e.g., Runge-Kutta method.
PINNs oer an alternative way of solving such problems.
Consider the setup illustrated in Figure 2, where a neural network, with
timetas input, is trained to predict the corresponding statesy(t) as output.
The network’s training and prediction considers thattis within the time
horizont∈[0, T]. In this conventional architecture, initial conditions are
“trained” into the neural network weights, which means that the trained
network will work only with the speciedxed initial conditions. Thus, we
would have to train a new neural network if we want to solve an IVP for the
same system but with a dierent initial conditiony(0).
8+
Neural
Network
t y(t)
Figure 2: PINN structure for solving an IVP. The neural network maps the timetto the
state at this time:y(t).
4.1.1. Loss Function
The loss function for PINNs consists of two terms basically:
MSE=MSE y +MSE F (3)
While therst term,MSE y, serves to impose the initial condition on the
neural network by utilizing input data with corresponding output targets,
the second term,MSE F , is used to impose the physics of the system on
the neural network output by penalizing it for not satisfying the ODE. The
latter term acts as a regularization term by imposing a specic solution on
the neural network. In contrast, the goal of a traditional regularization term
is usually to penalize large magnitudes of the weights.
Initial Conditions
To impose the initial condition on the neural network, we create a training
data point (t, ˆy) consisting of an inputt= 0 to the neural network and a
corresponding target ˆy0 =y 0 for its output. Then,MSE y is calculated as
follows:
MSE y = 1
Ny
∥y(0)− ˆy0∥2 (4)
where:y(0) is the predicted output of the neural network for inputt= 0;N y
is the dimension ofyor the number of system states; and∥·∥is theℓ 2-norm.
Physics
The neural network output should satisfy the ODE for the entire time
horizon of interestt∈[0, T] for the network to adhere to the physics of
the underlying system. For this,N f input points,{t k :k= 1, . . . , N f }, are
randomly sampled covering the entire time horizon [0, T], yielding a dataset of
collocation points. For each collocation point, a forward pass of the PINN is
performed to calculate the corresponding outputy(t k). The resulting output
9+
is used to calculate the deviation from the ODE in a residual function named
F:
F(y) := ∂y
∂t −f(y) (5)
where therst term is the neural network outputy(t) dierentiated with
respect to its time input. This derivative is obtained using automatic dier-
entiation, for instance, using TensorFlow. The second term of this equation,
f(y), corresponds to the ODE calculated fory. If these two terms match,
our neural network’s solutionysatises the system model given by the ODE.
This residual functionFis applied to every collocation point and used to cal-
culate the physics-related lossMSE F :
MSE F = 1
Nf
Nf
k=1
1
Ny
F(y(tk))
2
(6)
The loss function dened in ( 3) can now be computed and used for train-
ing the PINN. If it can reproduce the initial condition, and the derivative
of the neural network output satises the ODE for the entire time interval,
[0, T], then the output of the PINN is a solution to the IVP.
4.1.2. Training
To train PINNs, we must minimize the total loss function in ( 3). This
minimization commonly employs a two-step strategy involving the Adam
optimizer followed by the Broyden-Fletcher-Goldfarb-Shanno (BFGS) opti-
mizer ( Fletcher, 2000). The BFGS optimizer utilizes the Hessian matrix to
determine the optimization direction, yielding more precise results by con-
sidering curvature in a high-dimensional space. However, if applied directly
without preceding it with the Adam optimizer, there is a risk of rapid con-
vergence to a local minimum for the residual without exploring other po-
tential solutions. To mitigate this, we use the Adam optimizer initially to
navigate away from local minima and subsequently rene the solution using
the more accurate BFGS. In the context of Physics-Informed Neural Net-
works (PINNs), which often involve high-dimensional problems, the limited-
memory version of BFGS (L-BFGS) is frequently employed to handle opti-
mization problems with a large number of variables, as encountered in deep
learning applications. This combined approach, involving a sequence of op-
timizers, has been successfully applied in physics-informed neural networks,
particularly for solving systems of partial dierential equations (PDEs), as
10+
demonstrated in prior studies ( Karniadakis et al. , 2021). We apply the same
methodology in the current study. Additionally, Taylor et al. (2022) present
a recent investigation on dierent optimizers for PINNs.
4.2. Physics-Informed Neural Nets for Control (PINC)
In the traditional PINN framework, the initial condition isxed and
does not support a varying control input. The framework initially proposed
in Antonelo et al. (2024) adds the initial condition and control signal as
inputs to the PINN, leading to the Physics Informed Neural Networks for
Control (PINC). This argumentation increases the input dimension of the
PINN, along with the time required for training, enabling the resulting neural
network to make predictions from any initial condition and control input.
Figure 3a illustrates the concept whereby the PINC maps the input time,
the initial condition, and control input to a state prediction at the input
timet.
NN
t
y(0)
u
y(t)
(a) PINC
NN
t
u
y(T)y(0)
(b) PINC in self-loop
Figure 3: Physics-informed Neural Networks for Control (PINC). Left: PINC network
with timet, initial conditiony(0), and control inputuas inputs. This neural network
can make predictions of the state at timetgiven any initial condition and control input.
Right: PINC network in self-loop mode, allowing for long-range simulations. The output
state prediction at the timet=Tis fed back as the initial condition of the PINC to make
a new prediction, progressingTseconds every iteration. A dierent control input may be
applied at every iteration. For therst iteration, the initial condition must come from the
outside, possibly measured from the actual system.
Some changes are needed for the training regime to account for the PINC’s
new inputs (see Figure 3). Namely, the training data input must be extended
11+
with the additional inputs and their ranges selected. For the control input
u, this should be the feasible range of the control input. The range for the
initial condition should contain the states that the system can reach so that
the neural network is trained to make predictions from any reachable state
during operation.
4.2.1. Loss Function
The loss function for PINC is similar to the one for the traditional PINN,
i.e., one component for the initial conditions and one for the physics-based
loss:
MSE=λ y ·MSE y +λ F ·MSE F (7)
The only dierence here is that we added scaling factors to both terms,
which may also be applied to the traditional PINN but was left out for easy
understanding. Here, the scaling factors are scalars, but the concept may
easily be extended to include individual scaling factors for each of the states
so that bothλ y andλ F can become vectors with the same dimension asy.
This scaling allows the selection of priority for training of the dierent states,
which may help obtain a better result.
Initial Conditions
For the traditional PINN, only one point was needed to train for the
initial condition. Now, however, our initial condition belongs to a range of
values, and we also need to consider dierent control inputs. We will create
a set of training data points{v j :j= 1, . . . , N t}, where each point contains
the inputs to the neural networkv j =

0,y j
0,u jT
. Therst term is the
timet, being 0 for all these data points because they represent the initial
condition.y j
0 andu j correspond to thej-th initial condition and control
signal, randomly sampled within their feasible ranges to formN t data points.
The target for each of these training data points is the initial condition, which
appears in the input: ˆyj =y j
0.
The loss for the initial conditions is then calculated as the MSE of all
these training data points:
MSE y = 1
Nt
Nt
j=1
1
Ny
y(vj)− ˆyj2
(8)
12+
Physics
The collocation points,{v k :k= 1, . . . , N f }, used to impose the ODE
on the PINC net also need to be extended with the new inputs, that is,
vk =

tk,y k
0,u kT
. All three elements of each collocation point are sampled
randomly from their respective domains.
The residual function needs a slight change to include the control input
uin the ODE function:
F(y) := ∂y
∂t −f(y,u) (9)
The physics-related loss termMSE F is the same as for the traditional
PINN, only diering in the extended input to the neural network (v k):
MSE F = 1
Nf
Nf
k=1
1
Ny
F(y(vk))
2
(10)
4.2.2. Long Range Simulations by Looping the PINC
The PINC is trained to make predictions within the time horizont∈
[0, T], but longer-range simulations are possible by utilizing the PINC several
times in a self-loop mode. First, we use the system’s current state to make
a prediction at timeT; then, we use this prediction as input to the PINC
to obtain a new prediction at time 2T. We can continue this feeding back
of the predicted state, simulatingTseconds at every iteration until reaching
the desired prediction time. Figure 3b illustrates how this works, feeding the
neural network output back as the initial condition, input to the network, in
the next time interval.
When used with MPC, the prediction timeTof the PINC will be selected
to match the length of a single step in the controller so that the PINC, with
inputt=T, will act as a function mapping the states between the time steps
of the MPC. With this setup, the PINC allows choosing a dierent control
input at every time step, which is perfect for MPC applications.
4.3. Model Predictive Control
In this work, Model Predictive Control (MPC) ( Huba et al. , 2011) will
be employed to control an oil well. To ensure that the predictions of the
MPC satisfy the system dynamics, we need a function that maps the current
state and control input to the state at the next time step. For example, for a
linear system, the prediction can be implemented by a state transition matrix
13+
obtained from the discretization of the system. For a non-linear system, such
as the well model, we can use a linearization of the model or a numerical
integration method. Here, the PINC serves as the function mapping the
current state and control input to the state at the next time step. As the
PINC contains non-linear functions (the activation functions), the resulting
MPC will be within the category called Non-linear MPC (NMPC).
In this work, the following formulation is considered for model predictive
control of an oil well:
min
N
i=1
(y[k+i]−y ref)T Q(y[k+i]−y ref)+
Nu−1
i=0
∆u[k+i] T R∆u[k+i] (11a)
subject to:
x[k+j+ 1] =F(x[k+j],u[k+j]), j= 0, . . . , N−1 (11b)
y[k+j] =F y(x[k+j],u[k+j−1]), j= 1, . . . , N(11c)
u[k+j] =u[k+j−1] +∆u[k+j], j= 0, . . . , N u −1 (11d)
u[k+j] =u[k+N u −1], j=N u, . . . , N−1 (11e)
h(x[k+j],y[k+j],u[k+j−1])≤0, j= 1, . . . , N(11f)
where: the prediction horizon of MPC isNsteps; the control input is allowed
to change for therstN u steps; equation ( 11a) denes the cost function of
the optimization problem, whereby the deviations of the output variables
from their references and the changes in control input are penalized;Qis
the weight matrix for the output deviations from their references;Ris the
weight matrix that penalizes the changes in control inputs for therstN u
iterations; equation ( 11b) ensures that the solution satises the dynamics of
the system,i.e.,Frepresents the PINC which maps, one time-step ahead,
states to the next ones;F y in equation ( 11c) is a function that maps the
state and control inputs to some output variabley, which is the variable
we wish to control (the states themselves or algebraic variables, such as the
bottom-hole pressure in the oil well).
Equation ( 11d) ensures that therstN u control inputs change by their
respective∆ufactor. While the control input is only allowed to change for
therstN u iterations, afterward, it remains constant and equal to the control
input at time stepN u according to equation ( 11e). Finally, equation ( 11f)
denes the inequality constraints for the controller. They can limit the value
of the control inputsuand also set bounds on states or other variables of
interest.
14+
4.4. Improved PINC
The improvements proposed for the PINC architecture in this paper,
which are presented below, consist of adding skip connections to improve
training and avoid vanishing gradients and changing the model’s ODE equa-
tion to make the training of PINCs with a physics-based loss function feasible.
4.4.1. Skip Connections
Since gradients can vanish unwittingly during PINC network training,
which decreases prediction performance, especially for the particular appli-
cation of oil well modeling, we propose to employ an improved PINC archi-
tecture in this section. Any strategy that improves the magnitude of the
gradients can greatly help train the neural network. One approach is to use
skip connections in the network architecture to avoid vanishing gradients, as
proposed by Wang et al. (2021). Besides the fully connected dense network,
their proposed structure adds two more layers called encoders. The input to
these encoder layers is the neural network input. In contrast, the output of
these encoders is used to calculate the activation of each layer in the fully
connected network, except for thenal layer. This skip-connection struc-
ture ensures that the output of each layer of the neural network is closely
connected to the input layer. Equation ( 12) expresses the mathematical for-
mulation of the proposed structure,
 U=ϕ(W 1X+b 1)
V=ϕ(W 2X+b 2) (12a)
 Z(1) =ϕ(W z,1X+b z,1)
A(1) =

1−Z (1)
⊙U+Z (1) ⊙V (12b)

Z(k) =ϕ

Wz,kA(k−1) +b z,k
,
A(k) =

1−Z (k)
⊙U+Z (k) ⊙V, k= 2, . . . , N L
(12c)
y=WA (NL) +b (12d)
where⊙denotes the Hadamard product, namely the element-wise product of
two matrices. The visual representation of the structure of skip connections
is depicted in Figure 4.
This structure implements a neural network withN L hidden layers ofN n
neurons each.Xis the input to the network, which, for our application, is a
vector containing the time, the initial condition, and the control input. The
inputXis projected into a higher dimensional space through the encoders
15+
X
X
X
U
Z(1)
V
W1,b1
Wz,1,bz,1
W2,b2
A(1) Z(2)
Wz,2,bz,2
A(2) A(N) yWz,N ,bz,N
Figure 4: Illustration of the improved neural network architecture for PINNs, as proposed
by Wang et al. (2021).Xis the input to the neural network, which is projected into a higher
dimensional space through the two encoder layers, resulting in the higher dimensional
vectorsUandV. For each layer of the main network, werst calculate the intermediate
activationZutilizing the weight matrix and bias vector of this layer, thenZis weighted
by the encoder outputsUandVto calculate thenal activationAof the layer.
layers by using their respective weights and biasesW 1,W 2,b 1, andb 2,
resulting in theN n dimensional vectorsUandV.ϕis the hyperbolic tangent
activation function.
Therst step for calculating the forward pass is a standard pass through
a dense layer to computeZ (1), as shown in Equation ( 12b). Then thisZ (1)
is weighted by element wise multiplication (⊙) with the encoder vectorsU
andV, to calculate the activationA (1) of therst layer. This propagation
continues through all the remainder of theN L layers. Thenal outputy
is calculated as a linear projection of the previous layer’s activation without
the weighting from the encoder layers.
4.4.2. Safeguarding the Learning Process
Some of the ODE equations used to calculateMSE F can lead to problems
during training, so some modications are needed for the neural network to
train reliably. Modifying the ODE equations constitutes a problem that
depends on the type of system we are interested in modeling with the PINC
network. It happens that the oil well’s ODEs have undesirable functions that
can cause the training process to crash. Two of these problems are addressed
in the following.
Tubing Friction Factor: Equation ( A.6b) is highly non-linear and not
dened for negative numbers inside the logarithm function. For the loga-
rithm argument to be negative, the Reynolds number in the tubing must
be suciently negative, which is not physically possible. However, such an
undesirable condition arises during the initial phase of the training. To sim-
16+
plify this equation and help accelerate learning, we replace the equation with
an approximation using a third-order polynomial in the region of interest of
Reynolds numbers, which can be found through test simulations.
During the initial training phase, the neural network will output poor
predictions that can be far from physically feasible values. We can then end
up with Reynolds numbers outside the interval for which the approxima-
tion wast. The most straightforward tweak is to truncate the Reynolds
number (calculated from the PINC prediction) to the selected interval. Be-
cause this truncation eliminates the dependency on the preceding variables,
it also reduces the quality of the gradients when the Reynolds number gets
truncated, but, in practice, the truncation works justne. Equation ( 13a)
formalizes the approximation resulting from the truncation of the Reynolds
number, withg(·) being the third-order polynomial approximation dened
in Equation ( 13b).
λtb(Retb) =



g(Retb,min), Re tb < Retb,min
g(Retb), Re tb,min ≤Re tb ≤Re tb,max
g(Retb,max), Re tb > Retb,max
(13a)
g(x) =ax 3 +bx 2 +cx+d (13b)
The numerical values for the polynomial coecients and the ranges of
Reynolds numbers used to generate these approximations are shown in Ta-
ble B.6. Appendix B provides more details on the implemented approxima-
tion. The oil well model also contains a friction factor for the bottom-hole
friction, utilizing the same equations. However, since theow from the reser-
voir is constant when calculating the Reynolds number here, this friction
factor is also constant and no changes are needed.
Square Root:The square root is another function that can cause nu-
merical problems, mainly during the initial phase of the training, because it
is not dened for negative numbers. If the neural network outputs state pre-
dictions that result in a negative value in one of the square roots in the ODE,
the resulting value will not be dened (“NaN” in Python). This “NaN” (Not
a Number) will propagate through the calculations, invalidating the whole
training.
The issue is resolved by simply applying the max(·) operator within these
functions to avoid negative values. Even though this tweak results in no
gradients for negative numbers, it worked well since this mainly occurs in
the initial iterations of the training. To avoid zero division error in other
17+
equations, it is helpful to set the lower limit of the square root input to some
small positive value (e.g., 10 −3), a threshold that can be found by trial and
error. This modied square root function is:
fsqrt(x) =

max{x,10 −3}(14)
4.5. Neural Network for Algebraic Variables
As we are interested in controlling the algebraic states of the oil well
model, for instance, the bottom-hole pressure or liquid production, we need
some means for obtaining the values of these variables as the current PINC
framework only outputs the state predictions.
Although PINC could be trained to output the algebraic variables di-
rectly, this would limit itsexibility, as additional algebraic variables would
require fully retraining the network from scratch. Thus, we propose to train
an independent, traditional feedforward neural network to predict the alge-
braic variableszfrom the statesy. The input to this neural network are
the statesyand the control inputu, while the output is one or more of the
algebraic variableszof the model. This setup is illustrated in Figure 5. This
new neural network is trained independently of the PINC. The hierarchical
architecture allows utilizing dierent algebraic variables in the MPC by sim-
ply training a new neural network without retraining the PINC model, which
is much slower and more complex.
PINC
t
y(0)
u
NN
y(T)
z(T)
Figure 5: Hierarchical architecture for computing algebraic variables from the states. An
additional, independently trained neural network is trained to predict the algebraic vari-
ables of the oil well, for instance, the bottom-hole pressure. The inputs to this supporting
network are the state predictions from the PINC and the control input.
As no dynamics are involved in calculating the algebraic variables from
the states, the PINN framework is unnecessary. Like the PINC, training data
18+
is sampled from the entire state and control-input space. The corresponding
target outputs (the values of the algebraic variables) are calculated using the
ODE equations. It is important to note that modeling the entire system in an
end-to-end manner with neural networks,i.e., mapping inputs to the desired
algebraic variables, allows the MPC implemented in CasADi 1 to leverage a
smooth and dierentiable function (i.e., the neural network itself) as the
system’s model. Thus, using a network model enables the computation of a
Jacobian without hindrances. CasADi solves the resulting NLP problem with
IPOPT ( W¨ achter and Biegler, 2006), an interior-point algorithm developed
for problems with smooth and twice dierentiable objective functions and
constraints. IPOPT is a robust NLP solver widely applied in NMPC and
optimal control.
Empirical observations revealed that relying solely on the ODE equations
to compute algebraic variables from the PINC’s state prediction presents
challenges for the MPC in CasADi. In practice, this approach proved inef-
fective, as the optimization algorithm in CasADi often crashed before com-
pleting a meaningful simulation, with no discernible pattern to the crashes. It
is likely that the nature of the equations, involving square roots, logarithms,
and maximum operators, occasionally caused the optimizer to crash. This
observation further underscores the rationale behind adopting the proposed
hierarchical architecture.
Particularly for our oil well application, this supporting neural network
will be trained to predict four algebraic variables based on the input from
PINC’s state predictions and control input,i.e., the desired outputzis a
four-dimensional vector:
•bottom-hole pressure(P bh): the subject of control for one MPC appli-
cation.
•Gas-lift injection rate(w G,in): a limited resource the controller needs
to take into account.
•Gas production(w G,res): it may need to be constrained as some plants
have limited capacity for processing gas.
•Liquid production(w L,res): it can be used for economic optimization.
1CasADi is an open-source tool for nonlinear optimization and algorithmic dierentia-
tion, which can be downloaded from https://web.casadi.org/
19+
4.6. PINC for the Oil Well
Figure 5 depicts the architecture chosen for the PINC, where the PINC
module employs the structure with skip connections. This PINC module
has three types of inputs: timet; two control inputs corresponding to the
production choke openingu 1 in ( A.1f) and the gas-lift valve openingu 2 in
(A.1a); and an initial condition corresponding to a three-dimensional vector
with the mass of gas in the annulusm G,an, mass of gas in the tubingm G,tb,
and mass of liquid in the tubingm L,tb. The physics-informed loss function
corresponds to Eq. ( 1) and equations from Appendix A . In total, the input
layer has six units, while the output layer has three units mapping the states
mG,an,m G,tb, andm L,tb at timet.
The NN module has a three-dimensional input layer, which receives the
output prediction of the PINC module of the same dimension,i.e., the pre-
dicted statesm G,an,m G,tb, andm L,tb at timet. It outputs a four-dimensional
vector consisting of the algebraic variables described in the previous section,
namelyP bh,w G,in,w G,res, andw L,res. The bottom-hole pressureP bh will be
subject to control in our experiments by manipulating the two control inputs
(valve openings).
4.7. Evaluation Metrics
4.7.1. Model Validation
During hyperparameter search, the trained PINC is evaluated on a val-
idation set to select the hyperparameter values that yield the best network
performance on unseen data. Thus, the MSE between the PINC output and
the Runge-Kutta (RK) simulation of the gas-lifted oil well, which represents
the actual system, denes the validation loss, namely:
MSE val = 1
NvalNy
Nval
i=1
N(T,y i
0,val,u i
val)− ˆyi
val
2
(15)
where:N y is the number of states of the model;N val = 100 is the number
of validation points drawn randomly considering the chosen ranges for the
initial conditionsy i
0,val and control inputsu i
val. The target points ˆyi
val are
feasible points obtained from RK simulation;N(T,y i
0,val,u i
val) is the PINC
network predictionT= 60 seconds ahead in time for validation pointi; and
∥·∥is theℓ 2-norm.
Due to the issue of running into negative values in square roots, the self-
looping simulation was not performed for model evaluation as proposed in
20+
(Antonelo et al. , 2024), since these simulations would quickly run into the
infeasible state for our application. We assume that if PINC can yield good
predictions from any initial condition (within the selected domain), it should
also perform well in self-loop.
4.7.2. Evaluation of Prediction and Control
The evaluation of PINC predictions consists of iterating the network in
self-loop mode, starting from random initial conditions and with a random
sequence of control inputs, and then comparing its prediction to a Runge-
Kutta simulation of the system. As we consider the ODE to represent the
system perfectly, the Runge-Kutta simulation will represent the actual be-
havior of the oil well. The performance will be evaluated both visually and
using the Integral of Absolute Error (IAE) onCsampling points along the
simulation:
IAE= 1
C
C
k=1
1
Ny
∥y[k]−r[k]∥,(16)
wherey[k] is the output of the PINC network at the sample pointkandr[k]
is the Runge-Kutta reference simulation at the same sample point.
5. Experimental Setup
An improved PINC with skip connections, as detailed in the previous
section, will be selected as a model of a gas-lifted oil well. Then, the control
of the bottom-hole pressure of the oil well is tackled by embedding the trained
PINC in a nonlinear MPC task.
This section presents the techniques and congurations implemented for
training a PINC network with the best hyperparameters and the setup for
applying nonlinear MPC using the trained PINC network.
5.1. Experimental Setup of PINC
5.1.1. Domain of Training Data
The training data and collocation points are generated as presented in
Section 4.1.1. In addition, the upper limit for the time inputtshould be the
prediction time of interest. For our application, the PINC prediction time is
the time of a single step of the MPC,i.e.,T= 60 seconds. For the control
input, the range corresponds to the feasible valve openings (production choke
and gas-lift valve openings). The range for the states was selected by running
21+
several Runge-Kutta simulations with dierent control inputs to determine
the reachable states during operation. For the oil well model, the resulting
domain of these data is a cube in the three-dimensional state space (m G,an,
mG,tb, andm L,tb), which may be suboptimal, as some volumes within this
cube may be infeasible (e.g., square root of a negative number). Infeasible
points in the randomly drawn points from this cube are removed by running
them through the ODE to check their feasibility. Excluding these infeasible
points from the cube yielded thenal training set for the states. Removing
these infeasible points was very important, especially for the second well
model.
For the initial condition (state), the procedure above is directly applied
to generate the respective training set. For the collocation points, however,
this procedure only veries that the initial condition is feasible, not that
the desired output prediction 60 seconds ahead of time exists. So, if the
initial condition is close to infeasibility and the control input is unfortunate,
the desired output may not be feasible. In practice, this worksne, but
improvements may be possible.
5.1.2. Hyperparameters Search
During the hyperparameter search, all tentative congurations were trained
10 times with distinct initializations of the network weights and biases. For
performance evaluation, the error on the validation set was considered.
Adam Learning Rate
For this search, we trained a PINC net with 5 hidden layers consisting
of 20 neurons each for 1,000 iterations using the following learning rates:
{1,4,7} ×10 −4,{1,4,7} ×10 −3, and{1,4} ×10 −2, resulting in the best
choice of 7×10 −3, which presented the lowest validation prediction error.
Number of Training Data Points and Collocation Points
Tond the numberN t of data points for the initial condition and the
numberN f of collocation points, the same network of 5 hidden layers of 20
neurons each was employed. For each training run, after 1,000 epochs of
Adam2, other 1,000 iterations of L-BFGS followed. Figure 6 shows plots of
2On average, using the Adam method in therst thousand iterations yielded lower pre-
diction validation error and faster training than using only L-BFGS optimization through
the whole training, although both errors were in the same order of magnitude.
22+
Figure 6: Validation error progression during PINC training with dierent combinations
for the values ofN t (no. of data points) andN f (no. of collocation points). In each subplot,
the lines represent the training evolution of ten randomly initialized neural networks. The
limits on the y-axis are the same for all the subplots. The best average performance was
attained withN t=1,000 andN f =10,000, wherein none of the training attempts terminated
prematurely.
the validation error during training of ten models for each combination ofN t
andN f . The y-axis has the same limits in all the plots. Some training exper-
iments terminate prematurely due to converging to a poor local minimum.
Considering both thenal validation error and the number of training trials
that fail, the best choice was the combinationN t=1,000 andN f =10,000.
PINC Architecture Search
Tond the right number of hidden layers and neurons per layer, a grid
search was executed for{2,4,6,8,10}layers and{10,20,30,40}neurons per
layer, where each network was trained for 1,000 epochs with Adam followed
by 1,000 iterations with L-BFGS (Figure 7). In a second step, the best
three networks (6·30, 6·40 and 10·30 layers and neurons) were trained
for additional 1,000 iterations with L-BFGS, yielding the architecture of 6
hidden layers of 30 neurons each with the lowest average validation loss.
23+
Figure 7: Search for the PINC architecture, presenting the validation error during the
training of ten neural networks for each conguration, consisting of the number of hidden
layers and neurons per layer. The best three networks are 6·30, 6·40, and 10·30 layers
and neurons per layer. The y-axis has the same limits in all the subplots.
5.2. Experimental Setup of the NN for Algebraic Variables
We performed a hyperparameter search tond the best NN architecture
for predicting the algebraic variables (the supporting neural network from
Figure 5). The structures tested were fully densely connected neural net-
works with 1-4 hidden layers, each containing 10, 20, 30, and 40 neurons.
Ten tests were conducted for each conguration, with dierent weight ini-
tializations, and trained for 5,000 iterations of L-BFGS. The validation set
was constructed by randomly sampling 10,000 points from the input space,
where the respective target values resulted from solving the oil-well ODE
equations. The network of 4 hidden layers of 30 neurons each achieved the
lowest validation error and was subsequently trained until convergence with
L-BFGS. However, to speed up the MPC, a smaller network could be em-
ployed with no signicant decrease in performance.
24+
5.3. MPC Setup
The MPC controller was implemented in CasADi, an open-source numer-
ical optimization framework 3.
The prediction horizonNof MPC depends on the control problem, which
was chosen so that the system reaches a steady state within the specied
prediction horizon. The time step of the predictions isT= 60 seconds for
all control applications.
In typical applications, the optimization system denes a steady state,
maximizing total oil production while adhering to system and physical con-
straints ( M¨ uller et al., 2022). The optimization system informs the resulting
bottom-hole pressure to the control system as a reference for tracking. This
pressure reaches its reference quickly and usually before the states stabilize.
This fast reference tracking happens because of innitely many combinations
of state values and control inputs that will keep the bottom-hole pressure at
the reference. Thus, a prediction horizon ofN= 50 minutes is needed in
this case. If the states run too far o, the system may end up in a region
of the state space where the model is not dened, or the MPC cannotnd
a solution to the optimization problem. To ensure that a steady state is
reached at the end of the prediction horizon, the control-input horizon is se-
lected shorter (N u = 45) than the prediction horizon (N u < N). In practice,
this means that the control input will be constant for the last 5 steps of the
prediction horizon. Also, through the weight matrixQ, an extra penalty
is added to thesenal reference deviations (last 5 steps), making the MPC
prioritizending a stable state rather than damping the transient response:
Qii =
 1, i∈{1, . . . ,45}
100, i∈{46, . . . ,50} , R=
103 0
0 10 3

(17)
Appendix C gives more details on the MPC implementation in CasADi.
6. Results
Three variations of the oil well model, with dierent values of parameters
as detailed in Appendix A , will be considered, but more results will be shown
only with therst model for brevity. The experiments below refer to therst
well model if not explicitly stated otherwise. Both the long-range prediction
3https://web.casadi.org/docs/#document-ocp
25+
Figure 8: Plot of the training loss and validation error of the PINC trained for prediction
of well 1. The PINC was trained for 1,000 epochs with Adam and then until convergence
with L-BFGS. Because the nature of computation for the training loss (composed of the
initial condition and physics-based loss) and validation error are distinct, the numeric
values of these two losses are not directly comparable. Thenal training loss is 7.48·10 −7
and the validation loss, 1.43·10 −6.
and nonlinear MPC with the improved PINC for a gas-lifted oil well will be
presented in this section.
6.1. Long-range Prediction for an Oil Well with the Improved PINC
The PINC used for prediction and control has 6 hidden layers of 30 neu-
rons each, as found previously in the hyperparameter search. For therst
well, Figure 8 reports the training loss and validation error during the training
of its PINC. The validation loss shown in thisgure consists of the average
(scaled) error over 100 predictions 60 seconds ahead of time.
The performance of the trained PINC was evaluated for 3,000 seconds,
with a sequence of random control inputs that changed every 60 seconds,
using the IAE as a performance measure. The PINC was put in a self-
loop for 50 iterations to obtain this simulation. Only the initial condition
and the sequence of control inputs were input to the PINC network so that
prediction errors would accumulate over the self-looping. Figure 9 shows the
long-range PINC prediction for therst well, where the blue line corresponds
to the Runge-Kutta simulation (represents the actual system’s behavior),
the dashed pink line gives the PINC prediction, and the larger pink dots
26+
Figure 9: A test simulation of long-range PINC prediction for 3,000 seconds for therst
well. A random sequence of control input, changing every 60 seconds, and axed (ran-
domly chosen) initial condition are fed to the PINC. The resulting predictions are shown
in pink, with the dots indicating each self-loop iteration. The blue line (in the upper
three plots) shows the actual state values obtained by the Runge-Kutta simulation. The
fourth plot shows the bottom-hole pressure predictions, generated by passing the PINCs
predictions through the supporting neural network trained to predict the algebraic states.
The bottom plot depicts the randomly generated control input sequence. The IAE for
the states is 0.00959, a bit below the average, as shown in Table 2, while the IAE for the
pressure is 0.2813 bar.
indicate the PINC output after each iteration of self-loop. While therst
three uppermost plots report the state predictions produced by the PINC, the
fourth one shows the bottom-hole pressure predictions generated by feeding
the PINCs predictions through the supporting neural network, which predicts
the algebraic states. The bottom-most plot depicts the randomly generated
control-input sequence.
Table 2 shows the average and standard deviation of the IAE (of scaled
variables) for 100 test simulations of long-range prediction (3,000 seconds
each), where each test simulation resembles the one from Figure 9, but with
dierent randomly generated control inputs. For therst well, the average
and highest IAE of all three states are 0.00994 and 0.0332 bar, respectively.
27+
Table 2: Average and standard deviation of the IAE of the prediction for all three states,
and average IAE of the bottom-hole pressure prediction, for three oil wells for 100 test
simulations of 3,000 seconds each, with randomly generated inputs. Only the pressure
uses the second network for algebraic variables.
IAE Well 1 Well 2 Well 3
average (states) 0.00994 0.00448 0.00185
standard deviation (states) 0.00621 0.00345 0.000325
average (pressure) 0.3087 0.2497 0.0656
Additionally, the average IAE of the bottom-hole pressure for therst well
is 0.3087 bar.
6.2. Nonlinear MPC of Oil Well with Improved PINC
Here, experiments on tracking the bottom-hole pressure with the im-
proved PINC and nonlinear MPC will be shown and compared to a linear
MPC of a model linearized at each timestep, namely SLMPC ( Appendix D ).
Figure 10 shows a simulation with two-step changes in the bottom-hole pres-
sure reference. The states are shown in thegure to demonstrate that they
settle after some time, even though they are not controlled or constrained
in any way (m G,an,m G,tb, andm L,tb). The bottom-hole pressure follows the
given reference very well for the PINC MPC controller, with an IAE of 0.038
bar. For comparison, SLMPC, a method that linearizes the ODE equation
at every iteration of the control loop, described in Appendix D , is also plot-
ted in blue, with an IAE of 0.058 bar. Notice that the biggest challenge in
this experiment corresponds to the initial timesteps, where the bottom-hole
pressure deviates from the reference for both controllers.
The same simulation was repeated several times with the addition of
white measurement noise with a standard deviation of 5% added to the state
measurements. Figure 11 shows an example of these simulations. Several
of these simulations were completed, and the IAE was computed for each.
The resulting average and standard deviation statistics are shown in Table 3,
along with the IAE of the noiseless experiment. Regarding the simulations
with measurement noise, Figure 12 reports the average response and the
standard deviation, calculated along the trajectory. Thisgure shows in the
solid line the average response, and the two shaded areas show one and two
standard deviation regions, which encompass approximately 68% and 95%
of the simulations, respectively.
28+
Figure 10: Controlling the bottom-hole pressure (P bh): simulation of three-step changes
of 2 bar to the bottom-hole pressure reference (95 to 99 bar) for the PINC MPC in pink
and the SLMPC in blue. For the control input in the bottom-most plot, the PINC MPC
control input is shown in solid lines, and the SLMPC in dashed lines. The upper three
plots show the states that are not controlled or constrained (m G,an,m G,tb, andm L,tb). The
IAE of the PINC and SLMPC are 0.038 [bar] and 0.058 [bar], respectively.
6.3. Ablation of the Skip Connections
In this section, we investigate how skip connections aect the training
of PINC. Figure 13 shows the Kernel Density Estimate (KDE) plot for the
gradients of the residualF(·) dened in ( 9), for two PINCs with six layers
that are partially trained, one with skip connections (improved structure) and
another without them (normal structure). The plots show the distribution of
the gradients centered around zero for the weights and biases in all the layers.
A high spike at the curve’s center means that many of the gradients are near
zero, which is undesirable. The orange line isat whereas the blue line is
vertical, showing that the gradients obtained with the improved structure are
much better than the gradients of the normal structure, endorsing the use
of skip connections to improve training. In particular, the improved PINC
increased the magnitude of the gradient in thenal layer by four orders of
magnitude.
29+
Figure 11: Controlling the bottom-hole pressure (P bh) with the addition of measurement
noise. In the bottom plot, the PINC MPC control input is shown in solid lines, and the
linearized MPC is shown in dashed lines. The IAE of the PINC and SLMPC are 0.317
[bar] and 0.327 [bar], respectively.
Additionally, Figure 14 shows the validation error during training of 10
traditional networks in blue line and 10 networks with skip connections in
gray, where the dots indicate the endpoint of the training. All networks were
trainedrst with 500 epochs of Adam, followed by 500 iterations of L-BFGS.
Six neural networks, three of each type, converged before completing the 500
iterations of L-BFGS. As the L-BFGS implementation evaluates the loss on
average around three times per iteration, 500 iterations of L-BFGS translates
to almost 2000 in the plot. The interesting part of Figure 14 is that for all
seven networks where the training does not stop early, the new structure with
skip connections outperformed the normal structure, reducing the validation
error 67% on average. In our particular and challenging application of oil
well modeling, the skip connections clearly improved training. Further, as
the average success rate for training PINC without skip connections for the
oil well is quite low, we have not shown the control results for this normal
architecture.
30+
Table 3: IAE of simulations with the two MPCs. The 0% noise experiment is the one
shown in Figure 10, while the 5% noise statistics are calculated from several simulations,
one of which is shown in Figure 11.
Noise PINC MPC SLMPC
0% IAE 0.038 0.058
5% IAE average 0.339 0.297
IAE standard deviation 0.0200 0.0207
Figure 12: Controlling the bottom-hole pressure (P bh) in several simulations with mea-
surement noise: the average response and the standard deviation are plotted for both
controllers. The upper (lower) plot shows the results of the PINC MPC (SLMPC) con-
troller, where the innermost shaded area includes one standard deviation of the response
(around 68% of the total), and the outer shaded area corresponds to two standard devia-
tions of the response (around 95% of the total).
7. Conclusion
This work proposed an improved version of Physics-Informed Neural Net-
works for Control (PINC) of dynamic systems represented by ODEs. The
improvements addressed a class of more realistic and complex dynamic sys-
tems, such as gas-lifted oil wells, characterized by highly nonlinear terms
and functions not dened for negative numbers. These terms restrain the
training as the gradients of the physics-loss function, which contains these
terms, become less informative. The extensions proposed for PINC consist
of (i) using a particular neural network architecture based on skip connec-
tions, which improves the magnitude of the gradients during the training of
31+
Figure 13: Kernel Density Estimate (KDE) plot comparing the gradients concerning the
weights and biases of the residual functionF(·) dened in (9). The dierence between the
two PINC architectures is so expressive that the distributions of gradients for the normal
structure (blue) seem like vertical lines compared to the orange horizontal lines for the
improved structure (orange, with skip connections). For the last hidden layer (Layer 6),
the average magnitude of the gradients for the normal structure is 2.16·10 −4, while for
the improved structure, it is 2.55 (increasing by four orders of magnitude).
PINCs, avoiding known gradient pathologies in PINNs ( Wang et al. , 2021);
(ii) modifying the ODE equations to avoid pitfalls for use in the loss function;
and (iii) integrating a supporting feedforward neural network for learning the
static mappings between system’s states and algebraic variables.
Our proposed enhanced PINC achieved superior performance, averaging
a 67% reduction in the validation prediction error for the oil well application
compared to the original PINC. Additionally, it substantially improved the
gradientow through the network layers, increasing its magnitude by four
orders of magnitude.
The results showed that the PINC framework can be successful in mod-
eling and controlling complex systems with MPC, such as gas-lifted oil wells.
PINC allowed for an open-ended long-range prediction of the system with-
out access to the ODE (only used during training) and rendered the PINN
32+
Figure 14: Results for the ablation of skip connections. Validation MSE through training of
20 neural networks, 10 with the normal dense structure and 10 with the improved structure
(with skip connections). All networks were trained for 500 epochs of Adam, followed by
500 iterations of L-BFGS. The larger dots indicate the endpoints of the training, either
by early convergence or by completing the 500 iterations of L-BFGS. Three networks
of each type terminate training early. For the remainder, the improved neural network
structure outperforms the standard/normal structure, reducing the validation error by
67% on average.
amenable to a control scenario where the bottom-hole reference was followed.
Future work will investigate using adaptive scaling factorsλ y andλ F in
the loss function, which is known to improve the training of PINNs ( Xi-
ang et al. , 2022). Further, PINC could be applied to systems with other
characteristics, for instance, where the reference changes continuously. The
application of PINC to systems described by PDEs is also a research topic
for future investigation.
Acknowledgments
The authors acknowledge the support from UTFORSK/Norway, CAPES/Brazil
(project #88881.153841/2017-01), and CNPq/Brazil (grant #308624/2021-
1).
33+
Table A.4: Parameters for the oil well model from Jahanshahi et al. (2012).
Symb. Description Values Units
Runiversal gas constant 8.314 J/(mol·K)
ggravity 9.81 m/s 2
µviscosity 3.64×10 −3 Pa·s
ρL liquid density 760 kg/m3
MG gas molecular weight 0.0167 kg/mol
Tan annulus temperature 348 K
Van annulus volume 64.34 m 3
Lan annulus length 2048 m3
Pgs gas source pressure 140 bar
Sbh cross-section below injection point 0.0314 m 2
Lbh length below injection point 75 m
Ttb injection point tubing temperature 369.4 K
GORmass gas oil ratio 0−
Pres reservoir pressure 160 bar
wres average massow from reservoir 18 kg/s
Dtb tubing diameter 0.134 m
Ltb tubing length 2048 m
Vtb tubing volume 25.03 m 3
ϵpiping supercial roughness 2.80×10 −5 m
PIproductivity index 2.47×10 −6 kg/(s·Pa)
Kgs gas-lift choke cons. 9.98×10 −5 −
Kinj injection valve cons. 1.40×10 −4 −
Kpr production choke cons. 2.90×10 −3 −
Appendix A. Well Model’s Remaining Equations
Appendix A.1. Parameters of oil well models
Table A.4 shows the model parameters used for the primary oil well,
which were extracted from Jahanshahi et al. (2012), except forϵwhich could
not be found in the article. Instead, it was collected from Jordanou (2019).
Several oil wells were constructed by altering the parameters of the model,
whose values are shown in Table A.5.
34+
Symb. Well 1 Well 2 Well 3
R8.314 8.314 8.314
g9.81 9.81 9.81
µ3.64×10 −3 3.64×10 −3 3.64×10 −3
ρL 760 760 730
MG 0.0167 0.0167 0.0167
Tan 348 335 360
Van 64.34 84.82 56.55
Lan 2048 2700 1800
Pgs 140 140 140
Sbh 0.0314 0.0314 0.0314
Lbh 75 75 40
Ttb 369.4 355.6 381.2
GOR0 0 0.2
Pres 160 165 157
wres 18 11 30
Dtb 0.134 0.130 0.134
Ltb 2048 2700 1800
Vtb 25.03 31.00 22.08
ϵ2.80×10 −5 2.80×10 −5 2.80×10 −5
PI2.47×10 −6 2.12×10 −6 3.89×10 −6
Kgs 9.98×10 −5 10.43×10 −5 3.89×10 −5
Kinj 1.40×10 −4 1.20×10 −4 1.78×10 −4
Kpr 2.90×10 −3 2.43×10 −3 3.22×10 −3
Table A.5: Parameters for all the wells. First column is equivalent to the model from
Table A.4
Appendix A.2. Massows
wG,in =K gsu2

ρG,in max(Pgs −P at,0) (A.1a)
wG,inj =K inj

ρG,an,b max(Pan,b −P tb,b,0) (A.1b)
wres =PImax(P res −P bh,0) (A.1c)
wL,res = (1−α m
G,tb,b)wres (A.1d)
wG,res =α m
G,tb,bwres (A.1e)
35+
wout =K pru1

ρmix,tb,t max(Ptb,t −P 0,0) (A.1f)
wL,out = (1−α m
G,tb,t)wout (A.1g)
wG,out =α m
G,tb,twout (A.1h)
The gasow entering the annulus isw G,in at the top, whilew G,inj is the
ow of gas leaving the annulus and entering the production tubing. The total
massow, liquidow, and gasow entering the production tubing from the
reservoir are given byw res,w L,res, andw G,res respectively. The total mass
ow, liquidow, and gasow leaving the production tubing at the top-side
arew out,w L,out, andw G,out respectively.
Appendix A.3. Pressures
Pan,t = RTamG,an
MGVa
(A.2a)
Pan,b =P an,t + mG,angLan
Van
(A.2b)
Ptb,t = ρG,tb,tRTtb
MG
(A.2c)
Ptb,b =P tb,t + ρmixgLtb +F tb (A.2d)
Pbh =P tb,b +F bh +ρ LgLbh (A.2e)
The equations above dene the pressureP an,t at the top and the pressure
Pan,b at the bottom of the annulus. Likewise,P tb,t andP tb,b correspond to
the pressure at the top and bottom of the tubing, respectively. Finally,P bh
is the bottom-hole pressure.
Appendix A.4. Densities
The densities of gas and liquid in the streams in the annulus and tubing,
when applicable, are given by the equations below.
ρG,an,b = Pan,bMG
RTan
(A.3a)
ρG,in = PgsMG
RTan
(A.3b)
36+
ρG,tb,t = mG,tb
Vtb +S bhLbh −m L,tb/ρL
(A.3c)
ρmix = mG,tb +m L,tb −ρ LSbhLbh
Vtb
(A.3d)
ρG,tb,b = Ptb,bMG
RTtb
(A.3e)
ρmix,tb,t =α L,tb,tρL + (1−α L,tb,t)ρG,tb,t (A.3f)
Appendix A.5. Mass/liquid fractions
αL,tb = mL,tb −ρ LSbhLbh
VtbρL
(A.4a)
αm
G,bh =GOR/(GOR+ 1) (A.4b)
αL,tb,b = wL,resρG,tb,b
wL,resρG,tb,b + (wG,inj +w G,res)ρL
(A.4c)
αL,tb,t = 2 αL,tb −α L,tb,b (A.4d)
αm
G,tb,t = (1−α L,tb,t)ρG,tb,t
αL,tb,tρL + (1−α L,tb,t)ρG,tb,t
(A.4e)
Appendix A.6. Velocities
UL,tb = 4(1−α m
G,bh)wres
ρLπD2
tb
(A.5a)
UG,tb = 4(wG,in +α m
G,bhwres)
ρG,tb,tπD2
tb
(A.5b)
Umix,tb = UL,tb + UG,tb (A.5c)
UL,bh = wres
ρLSbh
(A.5d)
These equations express the liquid, gas and mix velocities in the tubing,
and the liquid velocity in the bottom-hole.
37+
Appendix A.7. Friction terms
Retb = ρmix,tbUmix,tbDtb
µ (A.6a)
1√λtb
=−1.8 log 10
 ϵ/Dtb
3.7
1.11
+ 6.9
Retb

(A.6b)
Ftb = αL,tbλtbρmix,tbU
2
mix,tbLtb
2Dtb
(A.6c)
Rebh = ρLUL,bhDbh
µ (A.6d)
1√λbh
=−1.8 log 10
 ϵ/Dbh
3.7
1.11
+ 6.9
Rebh

(A.6e)
Fbh = λbhρLU
2
L,bhLbh
2Dbh
(A.6f)
These equations calculate the friction pressure-loss terms for the tubing
(A.6c) and the bottom-hole ( A.6f). For the bottom-hole friction calcula-
tions, the average massow from the reservoir, wres, is used, as can be seen
in Equation ( A.5d), resulting in Equations ( A.6d), ( A.6e) and ( A.6f) being
constant, which is another of the simplications made in the derivation of
the model to make it explicit.
Appendix A.8. Simplications and Discussion
Simplications were implemented in the algebraic equations in order to
avoid implicit terms, resulting in an explicit model in the form of a system of
ODE equations that can be simulated with methods such as Runge-Kutta.
Equations ( A.5a), ( A.5b) and ( A.5d) use the predened constant wres as
theow from the reservoir, which is one of the simplications in the model
derived in Jahanshahi et al. (2012) to avoid an implicit set of equations.
For the bottom-hole friction calculations, the average massow from
the reservoir, wres, is used, as can be seen in Equation ( A.5d), resulting
in Equations ( A.6d), ( A.6e) and ( A.6f) being constant, which is another
simplication in the derivation of the model to render it explicit.
38+
Equation (A.5b) relates the velocity of gas to the massow of gas injected
into the tubing (w G,inj), but the latter is replaced with the massow of gas
injected into the annulus through the gas-lift choke (w G,in). This allows
changes in the gas-lift choke opening to directly aect the velocities in the
tubing, the tubing friction loss, and the pressure at the bottom of the tubing,
which happens more quickly than the change in pressure at the bottom of the
annulus. The massow of gas injected into the tubingw G,inj is dependent on
the pressure dierence between the bottom of the annulus and the bottom of
the tubing. A change in the gas-lift choke opening has an immediate eect
on the gas injected into the tubing.
Table A.4 shows the model parameters of the primary oil well, which
were extracted from Jahanshahi et al. (2012), except forϵwhich could not
be found in the article and instead it was collected from Jordanou (2019).
Appendix B. Approximation of ODE of oil well model for PINC
Figure B.15 shows an example of the 3 rd-order polynomial approximation
of the friction factorλ tb as given by Equations ( 13a) and ( 13b), in comparison
to the model Equation ( A.4c). The range of Reynolds numbers for which the
approximation ist is: [13000,115000]. This third-order approximation was
found to resemble the original friction factor satisfactorily. It was veried
by comparing Runge-Kutta simulations with the original equations and this
approximation, in which there was no noticeable dierence between the two.
The numerical values for the coecients in Equation ( 13b) and the ranges
of Reynolds numbers in Equation ( 13a) used to generate these approxima-
tions are shown in Table B.6.
Table B.6: Table presenting the numerical values for the third-order polynomial approxi-
mations for the three oil wells, along with the interval of Reynolds numbers for which the
estimation wastted. The bottom row shows the factor for which each column element
should be multiplied, for example, for therst well:a=−1.78·10 −17.
a b c d Retb,min Retb,max
Well 1 −1.78 4.56−4.18 3.29 13000 115000
Well 2 −1.78 4.55−4.17 3.29 13000 115000
Well 3 −0.203 0.887−1.48 2.67 50000 160000
Factor 10−17 10−12 10−7 10−2
39+
Figure B.15: The third-order polynomial approximation of the tubing friction factor in
Equation ( A.6c) in orange compared with the real friction factor in blue. This plot shows
the approximation for therst well, which wastted on the interval [13000,115000] using
thecurve fitfunction of SciPy.
Appendix C. MPC implementation in CasADi
The MPC will be formulated as a general Non-Linear Programming (NLP)
problem using thecasadi.Opticlass. CasADi solves the resulting NLP
problem with IPOPT ( W¨ achter and Biegler, 2006). IPOPT is an interior-
point algorithm developed for problems with smooth and twice dierentiable
objective functions and constraints, which is widely applied in NMPC and
optimal control.
In the following code listing, line 1 creates an instance of this class, then
variables and parameters are added to theOptiobject:
1 opti = casadi . Opti ()
2 N_state =3
3 N_input =2
4 x = opti . variable ( N_state , N +1)
5 u = opti . variable ( N_input , N)
6 du = opti . variable ( N_input , N_u ) # change in u for each step
7 P_bh = opti . variable (1 , N)
8
9 x0 = opti . parameter ( N_state ,1)
10 u_last = opti . parameter ( N_input , 1)
11 P_bh_ref = opti . parameter (1 , N)
12 Q = opti . parameter ((N +1) , (N +1) )
40+
13 R = opti . parameter ( N_u * N_input , N_u * N_input )
Listing 1: Instantiating variables and parameters for MPC of the bottom-hole pressure.
Here,N stateis the number of states andN inputis the number of con-
trol inputs (production choke and gas-lift valve). This setup is for controlling
the bottom-hole pressure. Theopti.variable()type refers to variables of
the optimization problem, whileopti.parameter()regards the parameters
given to the MPC at every iteration, such as reference and weights.x0is the
current measured (or estimated) state value, andu lastis the last applied
control input, which is needed as we penalize the change in control input.
An important implementation detail regards ensuring that the variablesx
andP bhsatisfy the system dynamics. Code listing 2 shows that the function
opti.subject to()is used only on the state variable, which constrains the
solution to satisfy the system dynamics. Here,F()represents a trained
PINC network, a function that maps a state and control input to the state
60 seconds ahead of time. For the bottom-hole pressure, there is no need for
a constraint; an assignment operator is enough.F x to P bh()represents
the output of the second network trained to predict the algebraic variable
bottom-hole pressure based on the values of the states and control input.
By theopti.subject to()here as well, we add unduly complexity to the
optimization problem, which results in slower computation.
1 opti . subject_to (x [: ,0] == x0 )
2 for i in range (0 ,N): # ODE constraint
3 opti . subject_to (x[: ,i +1] == F(x[: ,i],u[: ,i]) ) # PINC
4
5 for i in range (0 , N):
6 P_bh [: ,i] = F_x_to_P_bh (x[: ,i+1] , u[: ,i]) # NN algebraic
Listing 2: Ensuring that the MPC solution satisfy the system dynamics.
Constraints are also needed to enforce the relationship between the control
inputsu[k] and the change in control inputs∆u[k], which is implemented by
the following code:
1 opti . subject_to (u [: ,0] == u_last + du [: ,0])
2 for i in range (0 , N_u -1) :
3 opti . subject_to (u[: ,i +1] == u[: ,i] + du [: ,i +1])
4 for i in range (N_u , N):
5 opti . subject_to (u[: ,i] == u[: , N_u -1])
Listing 3: Implementing control input change constraints.
41+
Therst line ensures that the last applied control input is considered,
while lines 2-3 enforce this relationship for the control input horizon. Finally,
lines 4-5x the control input for thenal steps ifN u < N.duis then used
in the cost function to penalize the control input change.
For therst simulation iteration, we need to know the current control
input or set therst elements of theRmatrix to zero. This second option
allows therst control input of the MPC prediction to take any value without
being penalized. Thisexibility can be useful when starting a simulation
from an initial condition and when a steady-state control input is unknown.
Appendix D. Successive Linearization based MPC (SLMPC)
Successive Linearization based MPC (SLMPC) is a controller that, at
every time step, linearizes the model around the operating point and solves
a linear MPC problem. This kind of controller was successfully applied to
chemical reactors ( Seki et al. , 2002) and variable stiness actuated robots
(Zhakatayev et al. , 2017).
At every iteration of the MPC, the system equations are linearized and
discretized around the current operating pointx k, current control inputu k,
and current control variabley k. The linearized model can then be written
as:
∆xk+j+1 =∆x k+j +A k∆xk+j +B k∆uk+j +δ k (D.1a)
yk+j =C k∆xk+j +D k∆uk+j +y k (D.1b)
∆xk+j =x k+j −x k,∆u k+j =u k+j −u k,(D.1c)
where:
Ak =T ∂f
∂xk
(xk,u k),B k =T ∂f
∂uk
(xk,u k),(D.2a)
δk =Tf(x k,u k), (D.2b)
Ck = ∂h
∂xk
(xk,u k),D k = ∂h
∂uk
(xk,u k),y k =h(x k,u k),(D.2c)
whereTis the discretization time step length,f(x,u) is the ODE system,
andhis a function that computes the output from the states and control
input:y=h(x,u). Then, the linear model in Equation ( D.1a) can replace
the PINC in the constraint of Equation ( 11b), and the linearized output
Equation ( D.1b) can be used to implement the constraint in Equation ( 11c).
42+
