#include "blendMeshDeformer.h"

#include <maya/MFnPlugin.h>

MStatus initializePlugin(MObject obj)
{
	MStatus status;

	MFnPlugin fnPlugin(obj, "Aaron Carlisle", "1.0", "Any");

	status = fnPlugin.registerNode("blendMesh",
		BlendMesh::id,
		BlendMesh::creator,
		BlendMesh::initialize,
		MPxNode::kDeformerNode); // specify it's a deformer node
	CHECK_MSTATUS_AND_RETURN_IT(status);

	return MS::kSuccess;
}

MStatus uninitializePlugin(MObject obj)
{
	MStatus status;

	MFnPlugin fnPlugin(obj);

	status = fnPlugin.deregisterNode(BlendMesh::id);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	return MS::kSuccess;
}