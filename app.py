from flask import Flask, render_template, request
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

app = Flask(__name__)

# Load tourism dataset
df = pd.read_csv("tourism_destinations.csv")


@app.route("/", methods=["GET", "POST"])
def home():

    recommendations = []
    budget = 0
    days = 1
    category = "All"
    error = ""

    if request.method == "POST":

        try:
            budget = float(request.form["budget"])
            days = int(request.form["days"])
            category = request.form["category"]

            # Validate user inputs
            if budget <= 0:
                error = "Please enter a budget greater than zero."

            elif days < 1 or days > 30:
                error = "Please enter travel duration between 1 and 30 days."

            else:
                # Calculate available budget per day
                daily_budget = budget / days

                # Filter destinations based on budget
                filtered = df[
                    df["Estimated_Daily_Budget_INR"] <= daily_budget
                ]

                # Filter by selected category
                if category != "All":
                    filtered = filtered[
                        filtered["Category"] == category
                    ]

                # Generate itinerary and budget details
                recommendations = filtered.to_dict("records")

                for place in recommendations:

                    attractions = str(place["Attractions"]).split(";")
                    attractions = [a.strip() for a in attractions if a.strip()]

                    if not attractions:
                        attractions = ["Explore the destination"]

                    # Create a day-wise itinerary
                    itinerary = []

                    for day in range(days):
                        first = attractions[(day * 2) % len(attractions)]
                        second = attractions[(day * 2 + 1) % len(attractions)]

                        itinerary.append({
                            "day": day + 1,
                            "places": [first, second]
                        })

                    place["itinerary"] = itinerary

                    # Calculate estimated total cost
                    daily_cost = float(
                        place["Estimated_Daily_Budget_INR"]
                    )

                    place["total_cost"] = daily_cost * days

                    # Illustrative budget breakdown
                    place["accommodation"] = round(
                        place["total_cost"] * 0.40
                    )
                    place["food"] = round(
                        place["total_cost"] * 0.30
                    )
                    place["transport"] = round(
                        place["total_cost"] * 0.30
                    )

                # Generate budget comparison chart
                if not filtered.empty:

                    plt.figure(figsize=(9, 4))

                    plt.bar(
                        filtered["Destination"],
                        filtered["Estimated_Daily_Budget_INR"]
                    )

                    plt.title("Recommended Destination Budget")
                    plt.xlabel("Destination")
                    plt.ylabel("Estimated Daily Budget (INR)")
                    plt.xticks(rotation=30)
                    plt.tight_layout()

                    plt.savefig("static/budget_chart.png")
                    plt.close()

        except ValueError:
            error = "Please enter valid numbers for budget and travel duration."

    return render_template(
        "index.html",
        recommendations=recommendations,
        budget=budget,
        days=days,
        category=category,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)