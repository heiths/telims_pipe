# To Use:

Download and unzip the repo.
Place telims_pipe directory in the maya scripts folder.

From there, simply import telims_repo to start using.

## To Use Autorig:
~~~ python
import telims_pipe
from pipe_ui import autorig_ui
autorig = autorig_ui.AutorigUI()
autorig.build_gui()
~~~
## Example Use of Repo:
~~~ python
import telims_pipe
from rig_tools import curve_joint_generator

gui = curve_joint_generator.CurveJointGenerator()
no_gui = curve_joint_generator.CurveJointGenerator(False, 20, False, True, "testing", "r", "arm")

# for reloading, just reload telims_pipe
reload(telims_pipe)
~~~
