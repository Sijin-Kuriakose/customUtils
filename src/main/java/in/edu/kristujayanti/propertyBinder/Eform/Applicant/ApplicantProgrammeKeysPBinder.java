package in.edu.kristujayanti.propertyBinder.Eform.Applicant;

import in.edu.kristujayanti.propertyBinder.KJUSYSPropertyBinder;

public enum ApplicantProgrammeKeysPBinder implements KJUSYSPropertyBinder {

;



    private final String property;
    private final String label;
    private final Class dataType;
    private final int minLength;
    private final int maxLength;

    private ApplicantProgrammeKeysPBinder(String property, String label, Class dataType, int minLength, int maxLength) {
        this.property = property;
        this.label = label;
        this.dataType = dataType;
        this.minLength = minLength;
        this.maxLength = maxLength;
    }

    private ApplicantProgrammeKeysPBinder(String property, String label, Class dataType) {
        this.property = property;
        this.label = label;
        this.dataType = dataType;
        this.minLength = -1;
        this.maxLength = -1;
    }

    public String getPropertyName() {
        return this.property;
    }

    public String getDisplayName() {
        return this.label;
    }

    public Class getDataType() {
        return this.dataType;
    }

    public Integer getMinLength() {
        return this.minLength;
    }

    public Integer getMaxLength() {
        return this.maxLength;
    }

    // $FF: synthetic method
    private static ApplicantProgrammeKeysPBinder[] $values() {
        return ApplicantProgrammeKeysPBinder.class.getEnumConstants();
    }
}
