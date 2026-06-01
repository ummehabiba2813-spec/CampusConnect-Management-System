from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Message
from accounts.models import User

@login_required
def inbox(request):
    messages = Message.objects.filter(receiver=request.user)
    return render(request, "messaging/inbox.html", {"messages": messages})

@login_required
def send_message(request, user_id):
    receiver = User.objects.get(id=user_id)
    if request.method == "POST":
        content = request.POST["content"]
        Message.objects.create(sender=request.user, receiver=receiver, content=content)
        return redirect("inbox")
    return render(request, "messaging/send.html", {"receiver": receiver})
