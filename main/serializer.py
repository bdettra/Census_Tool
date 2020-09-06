from rest_framework import serializers
from main import models


class ErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.error
        fields=("error_message","participant")

class ParticipantSerializer(serializers.ModelSerializer):
    error_set=serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model=models.participant
        fields=["first_name","last_name","SSN","DOB","DOH","DOT","DORH","excluded","gross_wages","eligible_wages",
        "hours_worked","EE_pre_tax_amount","ER_pre_tax_amount","EE_roth_amount","ER_roth_amount","EE_catch_up","ER_catch_up",
        "total_EE_deferral","total_ER_deferral","effective_deferral_percentage","selection","key_employee","eligible","participating",
        "contributing","engagement",'error_set']