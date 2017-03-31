#include "blendMeshDeformer.h"

MTypeId     BlendMesh::id( 0x00000232 );
MObject     BlendMesh::aBlendWeight;
MObject     BlendMesh::aBlendMesh;


BlendMesh::BlendMesh()
{
}


BlendMesh::~BlendMesh()
{
}


void* BlendMesh::creator()
{
    return new BlendMesh();
}


MStatus BlendMesh::deform( MDataBlock& data, MItGeometry& itGeo,
        const MMatrix& localToWorldMatrix, unsigned int geomIndex )
{
    MStatus status;

    MDataHandle hBlendMesh = data.inputValue( aBlendMesh, &status );
    CHECK_MSTATUS_AND_RETURN_IT( status );
    MObject oBlendMesh = hBlendMesh.asMesh();
    if ( oBlendMesh.isNull() )
    {
        return MS::kSuccess;
    }

    MFnMesh fnMesh( oBlendMesh, &status );
    CHECK_MSTATUS_AND_RETURN_IT( status );
    MPointArray blendPoints;
    fnMesh.getPoints( blendPoints );

    float blendWeight = data.inputValue( aBlendWeight ).asFloat();
    float env = data.inputValue( envelope ).asFloat();
    MPoint point;
    float w = 0.0f;
    for ( ; !itGeo.isDone(); itGeo.next() )
    {
        point = itGeo.position();
        w = weightValue(data, geomIndex, itGeo.index());

        point += (blendPoints[itGeo.index()] - point) * blendWeight * env * w;

        itGeo.setPosition(point);
    }

    return MS::kSuccess;
}


MStatus BlendMesh::initialize()
{
    MStatus status;

    MFnNumericAttribute nAttr;
    MFnTypedAttribute tAttr;

    aBlendMesh = tAttr.create( "blendMesh", "blendMesh", MFnData::kMesh );
    addAttribute( aBlendMesh );
    attributeAffects( aBlendMesh, outputGeom );

    aBlendWeight = nAttr.create( "blendWeight", "bw", MFnNumericData::kFloat );
    nAttr.setKeyable( true );
    nAttr.setMin( 0.0 );
    nAttr.setMax( 1.0 );
    addAttribute( aBlendWeight );
    attributeAffects( aBlendWeight, outputGeom );

    MGlobal::executeCommand( "makePaintable -attrType multiFloat -sm deformer blendMesh weights;" );

    return MS::kSuccess;
}
