#include "gaussianNode.h"

MTypeId GaussianNode::id(0x00000231);
MObject GaussianNode::aOutValue;
MObject GaussianNode::aInValue;
MObject GaussianNode::aMagnitued;
MObject GaussianNode::aMean;
MObject GaussianNode::aVariance;

GaussianNode::GaussianNode() // constructor
{
}

GaussianNode::~GaussianNode() // destructor
{
}

void* GaussianNode::creator()
{
	return new GaussianNode();
}

MStatus GaussianNode::compute(const MPlug& plug, MDataBlock& data)
{
	MStatus status;

	if (plug != aOutValue)
	{
		return MS::kUnknownParameter;
	}

	// inputs
	float inputValue = data.inputValue(aInValue, &status).asFloat();
	float magnitued = data.inputValue(aMagnitued, &status).asFloat();
	float mean = data.inputValue(aMean, &status).asFloat();
	float variance = data.inputValue(aVariance, &status).asFloat();
	
	if (variance <= 0.0f)
	{
		variance = 0.001f;
	}

	// Gaussian function: AE - (x-b)^2/2c^2
	float xMinusB = inputValue - mean;
	float output = magnitued * exp(-(xMinusB * xMinusB) / (2.0f * variance));

	// write back to data block
	MDataHandle hOutput = data.outputValue(aOutValue, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	hOutput.setFloat(output);
	hOutput.setClean();
	data.setClean(plug);

	return MS::kSuccess;
}


MStatus GaussianNode::initialize()
{
	MStatus status;
	MFnNumericAttribute nAttr;
	
	// output attribute
	aOutValue = nAttr.create("outValue", "outValue", MFnNumericData::kFloat);
	nAttr.setWritable(false);
	nAttr.setStorable(false);
	addAttribute(aOutValue);

	// input attribute
	aInValue = nAttr.create("inValue", "inValue", MFnNumericData::kFloat);
	nAttr.setKeyable(true);
	addAttribute(aInValue);
	attributeAffects(aInValue, aOutValue); // important, sets up the relationship

	// magnituted attribute
	aMagnitued = nAttr.create("magnitued", "magnitued", MFnNumericData::kFloat);
	nAttr.setKeyable(true);
	addAttribute(aMagnitued);
	attributeAffects(aMagnitued, aOutValue); 

	// magnituted attribute
	aMean = nAttr.create("mean", "mean", MFnNumericData::kFloat);
	nAttr.setKeyable(true);
	addAttribute(aMean);
	attributeAffects(aMean, aOutValue); 

	// variance attribute
	aVariance = nAttr.create("variance", "variance", MFnNumericData::kFloat);
	nAttr.setKeyable(true);
	addAttribute(aVariance);
	attributeAffects(aVariance, aOutValue); 

	return MS::kSuccess;
}
