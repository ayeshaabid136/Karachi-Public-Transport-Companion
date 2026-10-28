import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from transport.models import Stop, Route, RouteStop, SafetyAdvisory


class Command(BaseCommand):
    help = "Load transport data from routes_data.json"

    @transaction.atomic
    def handle(self, *args, **options):
        file_path = Path(__file__).resolve().parents[2] / "routes_data.json"

        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        stops = {}

        for item in data.get("stops", []):
            stop, _ = Stop.objects.update_or_create(
                name=item["name"],
                defaults={
                    "area": item.get("area", ""),
                    "latitude": item.get("latitude"),
                    "longitude": item.get("longitude"),
                },
            )
            stops[stop.name] = stop

        for item in data.get("routes", []):
            route, _ = Route.objects.update_or_create(
                number=item["number"],
                defaults={
                    "name": item["name"],
                    "fare": item["fare"],
                    "min_fare": item.get("min_fare", 30),
                    "first_bus_time": item["first_bus_time"],
                    "last_bus_time": item["last_bus_time"],
                    "frequency_minutes": item.get("frequency_minutes", 15),
                },
            )

            RouteStop.objects.filter(route=route).delete()

            for sequence, stop_data in enumerate(item["stops"], start=1):
                stop_name, minutes = stop_data
                stop = stops.get(stop_name)

                if stop is None:
                    stop = Stop.objects.get(name=stop_name)

                RouteStop.objects.create(
                    route=route,
                    stop=stop,
                    sequence=sequence,
                    minutes_from_previous=minutes,
                )

        SafetyAdvisory.objects.all().delete()

        for item in data.get("advisories", []):
            route = None
            stop = None

            if item.get("route"):
                route = Route.objects.filter(
                    number=item["route"]
                ).first()

            if item.get("stop"):
                stop = Stop.objects.filter(
                    name=item["stop"]
                ).first()

            SafetyAdvisory.objects.create(
                route=route,
                stop=stop,
                level=item["level"],
                message=item["message"],
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Data loaded successfully: "
                f"{Stop.objects.count()} stops, "
                f"{Route.objects.count()} routes, "
                f"{RouteStop.objects.count()} route stops, "
                f"{SafetyAdvisory.objects.count()} advisories."
            )
        )