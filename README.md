# To Use:

Download and unzip the repo.
Place userSetup.py in the scripts folder.

On first launch of Maya a dialog will pop-up, click browse. Search for wherever you unzipped telims_pipe, click save.
Two new menus will appear (TELIMS, Comet).

You won't need to do this step anymore.

The following guides are for use inside the repo. If you just want to use the tools, simply use the 'TELIMS' menu.

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
