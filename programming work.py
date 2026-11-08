#PROJECT TITLE
print("SURVEY DATA QUALITY CONTROL AND VALIDATION SYSTEM")

import csv
import math
import statistics


def read_survey_csv(file_path):
    survey_data = []

    with open(file_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        required_fields = [
            "Point_ID", "Easting", "Northing", "Elevation"
        ]

        if not reader.fieldnames or not all(
            field in reader.fieldnames for field in required_fields
        ):
            raise ValueError("CSV file has missing column headings.")

        for row in reader:
            survey_data.append(row)

    return survey_data


def detect_spatial_outliers(valid_records, threshold_distance=1000.0):
    if not valid_records:
        return [], []

    median_e = statistics.median(
        record["Easting"] for record in valid_records
    )

    median_n = statistics.median(
        record["Northing"] for record in valid_records
    )

    errors = []
    cleaned_records = []

    for record in valid_records:
        dx = record["Easting"] - median_e
        dy = record["Northing"] - median_n

        distance = math.hypot(dx, dy)

        if distance > threshold_distance:
            errors.append(
                f"Spatial outlier detected for point "
                f"{record['Point_ID']}: {distance:.2f} m "
                f"from the reference centre."
            )
        else:
            cleaned_records.append(record)

    return errors, cleaned_records


def validate_and_clean_survey_data(survey_data):
    errors = []
    valid_records = []
    seen_ids = set()
    seen_coords = set()

    for record in survey_data:
        point_id = str(record.get("Point_ID") or "").strip()
        has_error = False
        coordinates = {}

        if not point_id:
            errors.append("Missing survey point ID.")
            has_error = True

        elif point_id in seen_ids:
            errors.append(f"Duplicate point ID: {point_id}")
            has_error = True

        else:
            seen_ids.add(point_id)

        for field in ["Easting", "Northing", "Elevation"]:
            value = record.get(field)

            if value is None or str(value).strip() == "":
                errors.append(
                    f"Missing {field} for {point_id or 'unknown point'}."
                )
                has_error = True
                continue

            try:
                number = float(value)

                if not math.isfinite(number):
                    raise ValueError

                if field == "Easting" and not 100000 <= number <= 900000:
                   errors.append(f"Invalid Easting range for {point_id}.")
                   has_error = True

                if field == "Northing" and not 0 <= number <= 10000000:
                   errors.append(f"Invalid Northing range for {point_id}.")
                   has_error = True

                coordinates[field] = number

            except (ValueError, TypeError):
                errors.append(
                    f"Invalid {field} for {point_id or 'unknown point'}."
                )
                has_error = True

        if has_error:
            continue

        coord_key = (
            coordinates["Easting"],
            coordinates["Northing"]
        )

        if coord_key in seen_coords:
            errors.append(
                f"Duplicate coordinates for point {point_id}."
            )
            continue

        seen_coords.add(coord_key)

        valid_records.append({
            "Point_ID": point_id,
            "Easting": coordinates["Easting"],
            "Northing": coordinates["Northing"],
            "Elevation": coordinates["Elevation"]
        })

    outlier_errors, cleaned_records = detect_spatial_outliers(
        valid_records,
        threshold_distance=1000.0
    )

    errors.extend(outlier_errors)

    return errors, cleaned_records


def export_results(cleaned_data, errors, total_records):

    with open(
        "cleaned_survey.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        fieldnames = [
            "Point_ID", "Easting", "Northing", "Elevation"
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_data)

    with open("qc_report.txt", "w", encoding="utf-8") as file:

        file.write("SURVEY DATA QUALITY CONTROL REPORT\n")
        file.write("----------------------------------\n")

        file.write(f"Total records processed: {total_records}\n")
        file.write(f"Accepted records: {len(cleaned_data)}\n")
        file.write(
            f"Excluded records: {total_records - len(cleaned_data)}\n"
        )
        file.write(f"Errors detected: {len(errors)}\n\n")
        
        if total_records > 0:
            acceptance_rate = (len(cleaned_data) / total_records) * 100
            rejection_rate = (total_records - len(cleaned_data)) / total_records * 100
        else:
         acceptance_rate = 0
         rejection_rate = 0

        file.write(f"Acceptance rate: {acceptance_rate:.2f}%\n")
        file.write(f"Rejection rate: {rejection_rate:.2f}%\n\n")

        file.write("ERROR DETAILS\n")
        file.write("-------------\n")

        if errors:
            for error in errors:
                file.write(error + "\n")
        else:
            file.write("No errors found.\n")



def display_cleaned_survey_table(cleaned_data):

    print("\nCLEANED SURVEY DATA TABLE\n")

    print(
        f"{'Point ID':<15}"
        f"{'Easting':<18}"
        f"{'Northing':<20}"
        f"{'Elevation':<15}"
    )

    for record in cleaned_data:
        print(
            f"{record['Point_ID']:<15}"
            f"{record['Easting']:<18.2f}"
            f"{record['Northing']:<20.2f}"
            f"{record['Elevation']:<15.2f}"
        )


if __name__ == "__main__":

    input_file = "test_data_2.csv"

    sample_data = [
        {
            "Point_ID": "P101",
            "Easting": 500000,
            "Northing": 4000000,
            "Elevation": 102.5
        },
        {
            "Point_ID": "P102",
            "Easting": 500025.5,
            "Northing": 4000015.2,
            "Elevation": 103.1
        },
        {
            "Point_ID": "P103",
            "Easting": 500050.1,
            "Northing": 4000030.4,
            "Elevation": 104.8
        },
        {
            "Point_ID": "P102",
            "Easting": 500025.5,
            "Northing": 4000015.2,
            "Elevation": 103.1
        },
        {
            "Point_ID": "P105",
            "Easting": 500080,
            "Northing": "",
            "Elevation": 105.2
        },
        {
            "Point_ID": "P106",
            "Easting": "ABC",
            "Northing": 4000075,
            "Elevation": 106
        },
        {
            "Point_ID": "P999",
            "Easting": 550000,
            "Northing": 4500000,
            "Elevation": 250
        }
    ]

    try:
        raw_data = read_survey_csv(input_file)

        print("Survey data loaded from CSV file.")

    except FileNotFoundError:
        print("CSV file not found. Using demonstration data.")
        raw_data = sample_data

    except ValueError as error:
        print("Input file error:", error)
        raise SystemExit

    errors, cleaned_data = validate_and_clean_survey_data(raw_data)

    export_results(cleaned_data, errors, len(raw_data))

    display_cleaned_survey_table(cleaned_data)

    print("\nSURVEY DATA QUALITY CONTROL SYSTEM")
    print("----------------------------------")
    print("Total records:", len(raw_data))
    print("Accepted records:", len(cleaned_data))
    print("Excluded records:", len(raw_data) - len(cleaned_data))
    print("Errors detected:", len(errors))
    if raw_data:
        acceptance_rate = (len(cleaned_data) / len(raw_data)) * 100
        rejection_rate = (
            (len(raw_data) - len(cleaned_data)) / len(raw_data)
        ) * 100
    else:
        acceptance_rate = 0
        rejection_rate = 0

    print("\nSURVEY DATA QUALITY SUMMARY")
    print("Acceptance rate:", f"{acceptance_rate:.2f}%")
    print("Rejection rate:", f"{rejection_rate:.2f}%")
    print("\nProcessing completed successfully.")
    print("Cleaned data saved in cleaned_survey.csv")
    print("Quality control report saved in qc_report.txt")
