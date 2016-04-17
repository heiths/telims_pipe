# To Use:

Download and unzip the repo.
Place telims_pipe directory in the maya scripts folder.
Place userSetup.py in the scripts folder.

On first launch of Maya a dialog will pop-up, click browse. Search for telims_pipe, click save.
Two new menus will appear (TELIMS, Comet).

You won't need to do this step anymore.

## To Use Autorig:
~~~ python
import telims_pipe
from pipe_ui import autorig_ui

autorig = autorig_ui.AutorigUI()
autorig.build_gui()
~~~
## To Use Joint Renamer:
~~~ python
import telims_pipe
from pipe_ui import joint_renamer_ui

joint_renamer = joint_renamer_ui.JointRenamer()
~~~
## To Use Curve Joint Generator:
~~~ python
import telims_pipe
from rig_tools import curve_joint_generator

gui = curve_joint_generator.CurveJointGenerator()
no_gui = curve_joint_generator.CurveJointGenerator(False, 20, False, True, "testing", "r", "arm")
~~~
### reloading
~~~ python
# for reloading, just reload telims_pipe
reload(telims_pipe)
~~~
