from netbootmgr.hostdb.models import Host, Group
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import generic


class HostIndexView(generic.ListView):
    context_object_name = 'hosts'

    def get_queryset(self):
        return Host.objects.order_by('-id')


class HostDetailView(generic.DetailView):
    model = Host


class GroupIndexView(generic.ListView):
    context_object_name = 'groups'

    def get_queryset(self):
        return Group.objects.order_by('-id')


class GroupDetailView(generic.DetailView):
    model = Group


def index(request):
    hosts = Host.objects.order_by("-id")[:10]
    groups = Group.objects.order_by("-id")[:10]
    return render(request, 'hostdb/host_group_list.html', {'hosts': hosts, 'groups': groups})