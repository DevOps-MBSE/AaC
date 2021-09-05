package org.devopsfordefense.aac.archmodel;

public class DataEntry implements Comparable<DataEntry> {
    private int entryID;
    private DataType type;
    private String name;
    private Cardinality cardinality;

    public DataEntry(int entryID, DataType type, String name, Cardinality cardinality) {
        this.entryID = entryID;
        this.type = type;
        this.name = name;
        this.cardinality = cardinality;
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((cardinality == null) ? 0 : cardinality.hashCode());
        result = prime * result + entryID;
        result = prime * result + ((name == null) ? 0 : name.hashCode());
        result = prime * result + ((type == null) ? 0 : type.hashCode());
        return result;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj)
            return true;
        if (obj == null)
            return false;
        if (getClass() != obj.getClass())
            return false;
        DataEntry other = (DataEntry) obj;
        if (cardinality != other.cardinality)
            return false;
        if (entryID != other.entryID)
            return false;
        if (name == null) {
            if (other.name != null)
                return false;
        } else if (!name.equals(other.name))
            return false;
        if (type == null) {
            if (other.type != null)
                return false;
        } else if (!type.equals(other.type))
            return false;
        return true;
    }

    public int getEntryID() {
        return entryID;
    }

    public DataType getType() {
        return type;
    }

    public String getName() {
        return name;
    }

    public Cardinality getCardinality() {
        return cardinality;
    }

    @Override
    public int compareTo(DataEntry o) {
        if (this.equals(o)) {
            return 0;
        } else if (this.entryID < o.entryID) {
            return -1;
        } else {
            return 1;
        }
    }
}
