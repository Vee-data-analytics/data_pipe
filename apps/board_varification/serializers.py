from rest_framework import serializers
from .models import Customer, Product,Job_number ,Employee, KitInspection, SolderPasteInspection, FirstOffBoardInspection, LastBoardProducedInspection, Wastage


class Job_number(serializers.ModelSerializer):
    class Meta:
        model = Job_number
        fields='__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        
class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'name', 'role']  # Ensure 'role' is included

class KitInspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = KitInspection
        fields = '__all__'

class SolderPasteInspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolderPasteInspection
        fields = '__all__'

class FirstOffBoardInspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirstOffBoardInspection
        fields = '__all__'

class LastBoardProducedInspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LastBoardProducedInspection
        fields = '__all__'

class WastageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wastage
        fields = '__all__'

