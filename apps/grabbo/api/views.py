from django.shortcuts import get_object_or_404

from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
)
from rest_framework.response import Response

from ..models import (
    Company,
    Job,
)
from .serializers import JobSerializer


class BlacklistCompanyView(GenericAPIView):

    def post(self, request, *args, **kwargs):
        company_name = request.data.get('company_name')
        company = get_object_or_404(Company, name=company_name)
        company.is_blacklisted = True
        company.save()
        return Response()


class JobsListView(ListAPIView):
    serializer_class = JobSerializer

    def get_queryset(self):
        return Job.objects.filter(
            is_blacklisted=False,
            company__is_blacklisted=False,
        ).prefetch_related('salary', 'company', 'category', 'technology')
