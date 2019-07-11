from django.shortcuts import render
from itertools import chain
from django.db.models import Count, Sum, DurationField, ExpressionWrapper, F

from .models import *


def show_list_services(request, pk):

    tourist = Tourist.objects.get(id=pk)
    list_of_services = chain(
        # 1
        DatelineForHotel.objects.filter(
            tourist=tourist
        ).annotate(
            name=F('hotel__name'),
            num=ExpressionWrapper(F('time_to') - F('time_from'),
                                  output_field=DurationField()),
            cost=F('hotel__cost_for_one_day')
        ).values('name', 'time_from', 'time_to', 'num', 'cost'),

        # 2
        TimelineForNutrition.objects.filter(
            tourist=tourist
        ).annotate(
            name=F('nutrition__name'),
            num=Count('name'),
            cost=F('nutrition__cost')
        ).values('name', 'time_from', 'time_to', 'num', 'cost'),

        # 3
        TimelineForExcursion.objects.filter(
            tourist=tourist
        ).annotate(
            name=F('excursion__name'),
            num=Count('name'),
            cost=F('excursion__cost')
        ).values('name', 'time_from', 'time_to', 'num', 'cost')
    )

    num_day_in_hotel = DatelineForHotel.objects.filter(
        tourist=tourist
    ).annotate(num=ExpressionWrapper(F('time_to') - F('time_from'),
                                     output_field=DurationField()
                                     )
               ).values('num', 'hotel__cost_for_one_day')

    # Если запрос вернулся не пустой и турист жил в отеле
    if num_day_in_hotel:
        total_of_hotel = 0
        for i in num_day_in_hotel:
            # Если день заселения и выселения совпадает, платить все равно за сутки
            if i['num'].days == 0:
                i['num'].days = 1   
            total_of_hotel = total_of_hotel + i['num'].days * i['hotel__cost_for_one_day']
    else:
        total_of_hotel = 0

    total_of_nutrition = TimelineForNutrition.objects.filter(
        tourist=tourist
    ).aggregate(Sum('nutrition__cost'))['nutrition__cost__sum']
    if not total_of_nutrition:
        total_of_nutrition = 0
         
    total_of_excursion = TimelineForExcursion.objects.filter(
        tourist=tourist
    ).aggregate(Sum('excursion__cost'))['excursion__cost__sum']
    if not total_of_excursion:
        total_of_excursion = 0

    # Просуммируем стоимость всех услуг
    total = total_of_hotel + total_of_nutrition + total_of_excursion
    
    context = {
        'tourist': tourist,
        'list_of_services': list_of_services,
        'total': total
        }
    # Передаём HTML шаблону данные контекста
    return render(request, 'tourists/show_list_services.html', context=context)