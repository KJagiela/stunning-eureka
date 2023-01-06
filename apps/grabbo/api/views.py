from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Company


class BlacklistCompanyView(APIView):

    def post(self, request, *args, **kwargs):
        company_name = request.data.get('company_name')
        company = get_object_or_404(Company, name=company_name)
        company.is_blacklisted = True
        company.save()
        return Response()
