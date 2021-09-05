package org.devopsfordefense.aac.archmodel;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

/**
 * A Model is an logical element of a system of element of a system decomposition.
 * 
 */
public class ArchitectureModel {

    private final String name;
    private final ArchitectureModel parent;

    private final List<ArchitectureModel> children;

    /**
     * Constructor
     * 
     * @param name The name of this Model element.
     * @param parent The parent Model element of the architecture decomposition.  If null, this Model will be the root. 
     */
    public ArchitectureModel(String name, ArchitectureModel parent) {
        this.name = name;
        this.parent = parent;
        children = new ArrayList<ArchitectureModel>();
    }

    public String getName() {
        return name;
    }

    public ArchitectureModel getParent() {
        return parent;
    }

    public void addChild(ArchitectureModel child) {
        children.add(child);
    }

    public Iterator<ArchitectureModel> children() {
        return children.iterator();
    }
}