package org.devopsfordefense.aac.archmodel;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

public class DataModel {
    
    private final List<DataEntry> entries;

    public DataModel() {
        entries = new ArrayList<DataEntry>();
    }

    public void add(DataEntry dataEntry) {
        entries.add(dataEntry);
    }

    public Iterator<DataEntry> iterator() {
        return entries.iterator();
    }
}
