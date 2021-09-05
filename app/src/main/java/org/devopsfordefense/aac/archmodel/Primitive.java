package org.devopsfordefense.aac.archmodel;

public class Primitive implements DataType {

    private PrimitiveType type;

    @Override
    public String getTypeName() {
        return type.toString();
    }
}
