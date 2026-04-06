from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Product
from .serializers import ProductSerializer
from .paginations import ProductPageNumberPagination


class ProductViewSet(ViewSet):
    """
    상품 API ViewSet
    - 목록
    - 상세
    - 생성
    - 수정
    - 부분 수정
    - 삭제
    """

    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def list(self, request):
        queryset = Product.objects.all().order_by("-id")

        paginator = ProductPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)

        serializer = ProductSerializer(
            page,
            many=True,
            context={"request": request}
        )

        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        product = get_object_or_404(Product, pk=pk)

        serializer = ProductSerializer(
            product,
            context={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = ProductSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        product = get_object_or_404(Product, pk=pk)

        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=False,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def partial_update(self, request, pk=None):
        product = get_object_or_404(Product, pk=pk)

        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return Response({"message": "deleted"}, status=status.HTTP_204_NO_CONTENT)


class ProductListPageView(TemplateView):
    template_name = "products/product_list.html"


class ProductDetailPageView(TemplateView):
    template_name = "products/product_detail.html"


class ProductCreatePageView(TemplateView):
    template_name = "products/product_create.html"


class ProductUpdatePageView(TemplateView):
    template_name = "products/product_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pk"] = self.kwargs.get("pk")
        return context