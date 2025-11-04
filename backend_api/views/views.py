from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, permissions
from backend_api.serializers import  ContactSerializer, InvoiceSerializer




class AddContactView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Check if user is verified
        if not user.is_active:
            return Response({"detail": "Email not verified. Access denied."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateInvoiceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = InvoiceSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            invoice = serializer.save()
            return Response({
                "message": "Invoice created successfully",
                "bill_id": invoice.bill_id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


