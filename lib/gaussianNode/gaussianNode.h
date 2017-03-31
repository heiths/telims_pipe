#ifndef GAUSSIANNODE_H
#define GAUSSIANNODE_H

#include <maya/MPxNode.h>
#include <maya/MFnNumericAttribute.h>
#include <iostream>
#include <math.h>

class GaussianNode : public MPxNode
{
public:
	GaussianNode(); // constructor
	virtual ~GaussianNode(); // destructor
	static void* creator();

	virtual MStatus compute(const MPlug& plug, MDataBlock& data);
	static MStatus initialize();

	static MTypeId id;
	static MObject aOutValue;
	static MObject aInValue;
	static MObject aMagnitued;
	static MObject aMean;
	static MObject aVariance;
};

#endif
