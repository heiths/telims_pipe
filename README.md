# To Use:

Download and unzip repo.
Place telims_pipe directory in the maya scripts folder.

From there, simply import telims_repo to start using.

# Example:
import telims_pipe
from rig_tools import curve_joint_generator

gui = curve_joint_generator.CurveJointGenerator()
no_gui = curve_joint_generator.CurveJointGenerator(False, 20, False, True, "testing", "r", "arm")
