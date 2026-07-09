from rest_framework.response import Response

def api_success(data=None, message="Success", status=200):
    return Response({
        "success": True,
        "message": message,
        "data": data
    }, status=status)


def api_error(message="Error", status=400):
    return Response({
        "success": False,
        "message": message
    }, status=status)

def create_audit_log(user, action, target_model=None, target_id=None, description="", metadata=None):
    from .models import AuditLog
    AuditLog.objects.create(
        user=user if user and user.is_authenticated else None,
        action=action,
        target_model=target_model,
        target_id=str(target_id) if target_id else None,
        description=description,
        metadata=metadata if metadata else {}
    )