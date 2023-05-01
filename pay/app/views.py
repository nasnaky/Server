import jwt
from django.db.models import Q

from rest_framework import status, pagination
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.contrib.auth.models import User

from .serializers import *


class UserRegistrationView(CreateAPIView):
    serializer_class = UserRegistrationSerializer
    queryset = serializer_class.Meta.model.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "meta": {
                "code": 201,
                "message": "CREATED"
            },
            "data": {
                "message": "생성이 완료됐습니다."
            }
        }, status=status.HTTP_201_CREATED)


def is_valid_jwt(token):
    try:
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return True
    except jwt.exceptions.ExpiredSignatureError:
        return False
    except jwt.exceptions.InvalidTokenError:
        return False


def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_email = payload['user_id']
        return user_email
    except jwt.exceptions.DecodeError:
        return None


class ProductView(APIView):
    def post(self, request):
        if is_valid_jwt:
            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid():
                token = request.META.get('HTTP_AUTHORIZATION')
                user = User.objects.get(pk=decode_jwt_token(token))
                serializer.save(user=user)
                return Response({
                    "meta": {
                        "code": 201,
                        "message": "생성이 완료되었습니다."
                    },
                    "data": None
                }, status=status.HTTP_201_CREATED)
            return Response({
                "meta": {
                    "code": 400,
                    "message": "잘못된 요청 입니다.."
                },
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "meta": {
                "code": 400,
                "message": "잘못된 토큰 입니다.."
            },
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    def get(self, request, pk):
        if is_valid_jwt:
            token = request.META.get('HTTP_AUTHORIZATION')
            user = User.objects.get(pk=decode_jwt_token(token))
            product = PRODUCT.objects.get(pk=pk)
            if product.user == user:
                serializer = ProductSerializer(product)
                return Response({
                    "meta": {
                        "code": 200,
                        "message": "ok"
                    },
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                "meta": {
                    "code": 400,
                    "message": "유저가 다릅니다."
                },
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "meta": {
                "code": 400,
                "message": "잘못된 토큰 입니다.."
            },
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        if is_valid_jwt:
            token = request.META.get('HTTP_AUTHORIZATION')
            user = User.objects.get(pk=decode_jwt_token(token))
            product = PRODUCT.objects.get(pk=pk)
            serializer = ProductSerializer(product, data=request.data)
            if serializer.is_valid():
                if product.user == user:
                    serializer.save()
                    return Response({
                        "meta": {
                            "code": 200,
                            "message": "수정이 완료되었습니다."
                        },
                        "data": None
                    }, status=status.HTTP_201_CREATED)
                return Response({
                    "meta": {
                        "code": 400,
                        "message": "유저가 다릅니다."
                    },
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                "meta": {
                    "code": 400,
                    "message": "잘못된 요청 입니다.."
                },
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "meta": {
                "code": 400,
                "message": "잘못된 토큰 입니다.."
            },
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if is_valid_jwt:
            token = request.META.get('HTTP_AUTHORIZATION')
            user = User.objects.get(pk=decode_jwt_token(token))
            product = PRODUCT.objects.get(pk=pk)
            if user == product.user:
                product.delete()
                return Response({
                    "meta": {
                        "code": 204,
                        "message": "삭제가 완료됐었습니다."
                    },
                    "data": None
                }, status=status.HTTP_204_NO_CONTENT)
            return Response({
                "meta": {
                    "code": 400,
                    "message": "유저가 다릅니다."
                },
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "meta": {
                "code": 400,
                "message": "잘못된 토큰 입니다.."
            },
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


class MyPagination(pagination.PageNumberPagination):
    page_size = 10


class ProductListView(APIView):
    def get(self, request):
        if is_valid_jwt:
            token = request.META.get('HTTP_AUTHORIZATION')
            user = User.objects.get(pk=decode_jwt_token(token))
            paginator = MyPagination()
            queryset = PRODUCT.objects.filter(user=user).order_by('-id')
            result_page = paginator.paginate_queryset(queryset, request)
            serializer = ProductListSerializer(result_page, many=True)
            return Response({
                "meta": {
                    "code": 200,
                    "message": "ok"
                },
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "meta": {
                "code": 400,
                "message": "잘못된 토큰 입니다.."
            },
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


class ProductSearchView(APIView):
    def get(self, request):
        if is_valid_jwt:
            token = request.META.get('HTTP_AUTHORIZATION')
            user = User.objects.get(pk=decode_jwt_token(token))
            query = request.query_params.get('query', '')
            queryset = PRODUCT.objects.filter(Q(name__icontains=query) and Q(user=user)).order_by('-id')
            queryset |= PRODUCT.objects.filter(Q(name__startswith=query) and Q(user=user)).order_by('-id')
            paginator = MyPagination()
            result_page = paginator.paginate_queryset(queryset, request)
            serializer = ProductListSerializer(result_page, many=True)
            return Response({
                "meta": {
                    "code": 200,
                    "message": "ok"
                },
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "meta": {
                "code": 400,
                "message": "잘못된 토큰 입니다.."
            },
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)
