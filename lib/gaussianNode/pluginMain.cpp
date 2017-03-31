#include "gaussianNode.h"
#include <maya/MFnPlugin.h>

MStatus initializePlugin(MObject obj)
{
	MStatus status;
	MFnPlugin fnPlugin(obj, "Aaron Carlisle", "1.0", "any");

	status = fnPlugin.registerNode("gaussian",
		GaussianNode::id,
		GaussianNode::creator,
		GaussianNode::initialize);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	
	return MS::kSuccess;
}

MStatus uninitializePlugin(MObject obj)
{
	MStatus status;
	MFnPlugin fnPlugin(obj);

	status = fnPlugin.deregisterNode(GaussianNode::id);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	return MS::kSuccess;
}