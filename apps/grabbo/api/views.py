from django.shortcuts import get_object_or_404

from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
)
from rest_framework.response import Response

from ..models import (
    HypeStatus,
    Job,
)
from .serializers import JobSerializer


class ChangeJobStatusView(GenericAPIView):

    def post(self, request, *args, **kwargs):
        job_id = kwargs.get('id')
        company = get_object_or_404(Job, id=job_id)
        company.status = request.data.get('hype')
        company.save()
        return Response()


class JobsListView(ListAPIView):
    serializer_class = JobSerializer

    def get_queryset(self):
        return (
            Job.objects
            .exclude(status=HypeStatus.FUCK_IT, company__status=HypeStatus.FUCK_IT)
            .prefetch_related('salary', 'company', 'category', 'technology')
        )
