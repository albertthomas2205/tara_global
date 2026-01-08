from rest_framework import serializers
from .models import Student,Subject,PDFDocument,Lastmodule
from .bunnycdn_utils import BunnyCDNUploader
from django.conf import settings
from django.utils import timezone

# Get BunnyCDN config from settings
BUNNY_CDN_STORAGE_ZONE = settings.BUNNY_CDN_STORAGE_ZONE
BUNNY_CDN_URL = settings.BUNNY_CDN_URL
BUNNY_API_KEY = settings.BUNNY_API_KEY

# Initialize the BunnyCDN uploader
bunny_cdn = BunnyCDNUploader(
    api_key=BUNNY_API_KEY,
    storage_zone=BUNNY_CDN_STORAGE_ZONE,
    base_url=BUNNY_CDN_URL,
)

class StudentSerializer(serializers.ModelSerializer):
    # Field for file upload (write-only)
    image_file = serializers.FileField(write_only=True, required=False)
    
    # The image field will be read-only and show the URL
    image = serializers.URLField(read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'user', 'student_id', 'name', 'image', 'image_file']

    def create(self, validated_data):
        print("function called created")
        print("validated data = ", validated_data)

        # Pop the file from validated_data (use image_file for upload)
        file = validated_data.pop("image_file", None)
        
        # Create student instance first
        student = Student.objects.create(**validated_data)

        if file:
            uploaded_url = bunny_cdn.upload_file(file)
            if uploaded_url:
                student.image = uploaded_url
                student.save()
                print(f"Image uploaded successfully: {uploaded_url}")
            else:
                print("Image upload failed")
        else:
            print("no file found")

        return student

    def update(self, instance, validated_data):
        file = validated_data.pop("image_file", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if file:
            uploaded_url = bunny_cdn.upload_file(file)
            if uploaded_url:
                instance.image = uploaded_url

        instance.save()
        return instance
    


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id','user',  'name'] 


class PDFDocumentSerializer(serializers.ModelSerializer):
    file_upload = serializers.FileField(write_only=True, required=False)
    ppt_upload = serializers.FileField(write_only=True, required=False)

    file = serializers.URLField(read_only=True)
    ppt_file = serializers.URLField(read_only=True)

    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = PDFDocument
        fields = [
            'id',
            'subject',
            'subject_name',
            'module_name',
            'file',
            'ppt_file',
            'file_upload',
            'ppt_upload',
            'uploaded_at'
        ]

    # ✅ Create logic (no replace if already exists)
    def create(self, validated_data):
        subject = validated_data.get('subject')
        module_name = validated_data.get('module_name')
        pdf_file = validated_data.pop('file_upload', None)
        ppt_file = validated_data.pop('ppt_upload', None)

        # Prevent duplicates
        if PDFDocument.objects.filter(subject=subject, module_name=module_name).exists():
            raise serializers.ValidationError({
                "detail": "A document already exists for this subject and module."
            })

        pdf_doc = PDFDocument.objects.create(**validated_data)

        # Upload PDF
        if pdf_file:
            uploaded_pdf_url = bunny_cdn.upload_file(pdf_file)
            if uploaded_pdf_url:
                pdf_doc.file = uploaded_pdf_url
            else:
                raise serializers.ValidationError({"file_upload": "PDF upload failed!"})

        # Upload PPT
        if ppt_file:
            uploaded_ppt_url = bunny_cdn.upload_file(ppt_file)
            if uploaded_ppt_url:
                pdf_doc.ppt_file = uploaded_ppt_url
            else:
                raise serializers.ValidationError({"ppt_upload": "PPT upload failed!"})

        pdf_doc.uploaded_at = timezone.now()
        pdf_doc.save()
        return pdf_doc

    # ✅ Update logic (replace files if re-uploaded)
    def update(self, instance, validated_data):
        pdf_file = validated_data.pop('file_upload', None)
        ppt_file = validated_data.pop('ppt_upload', None)

        # Update normal fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # If new PDF uploaded → replace old one
        if pdf_file:
            uploaded_pdf_url = bunny_cdn.upload_file(pdf_file)
            if uploaded_pdf_url:
                instance.file = uploaded_pdf_url
            else:
                raise serializers.ValidationError({"file_upload": "PDF upload failed!"})

        # If new PPT uploaded → replace old one
        if ppt_file:
            uploaded_ppt_url = bunny_cdn.upload_file(ppt_file)
            if uploaded_ppt_url:
                instance.ppt_file = uploaded_ppt_url
            else:
                raise serializers.ValidationError({"ppt_upload": "PPT upload failed!"})

        instance.uploaded_at = timezone.now()
        instance.save()
        return instance

    def validate_file_upload(self, value):
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("Only PDF files are allowed.")
        return value
    
    
class LastmoduleSerializer(serializers.ModelSerializer):
    pdf = serializers.PrimaryKeyRelatedField(queryset=PDFDocument.objects.all())

    class Meta:
        model = Lastmodule
        fields = ['id', 'pdf']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # Replace the PDF ID with full serialized data
        rep['pdf'] = PDFDocumentSerializer(instance.pdf, context=self.context).data
        return rep
    

