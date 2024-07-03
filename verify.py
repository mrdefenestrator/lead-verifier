#!/usr/bin/env python3
import csv
import sys
import webbrowser

def rec_prompt(prompt):
    val = input(f"{prompt} (y/n): ")
    if val not in ('y', 'n'):
        return rec_prompt(prompt)
    return val == "y"

def main():
    inpath = sys.argv[1]
    outpath = sys.argv[2]
    in_rows = []
    out_rows = []
    initialized_file = False
    verified_col = 'verified'

    verified_urls = set()
    not_verified_urls = set()

    # read the file into rows
    with open(inpath, 'r') as fp:
        reader = csv.reader(fp)

        header = reader.__next__()
        if header[-1] == verified_col:
            initialized_file = True
        url_offset = header.index("URL")

        out_rows = []
        for row in reader:
            in_rows.append(row)

    try:
        # Make a decision on each of the rows
        for row in in_rows:
            url = row[url_offset]

            if url in verified_urls:
                # We've already seen this url and verified it
                verified = True
            elif url in not_verified_urls:
                # We've already seen this url and not verified it
                verified = False
            elif initialized_file and row[-1] == 'y':
                # We've previously seen this and verified it
                verified = True
            elif initialized_file and row[-1] == 'n':
                # We've previously seen this and not verified it
                verified = False
            else:
                # We need to view and verify this role
                print(row)
                webbrowser.open(f"http://{url}", new=0, autoraise=True)
                verified = rec_prompt("Is this relevant?")

            if initialized_file:
                # need to write into cell for our decision
                row[-1] = 'y' if verified else 'n'
            else:
                # need to append cell our decision
                row.append('y' if verified else 'n')

            # cache the decision on the url
            if verified:
                verified_urls.add(url)
            else:
                not_verified_urls.add(url)

            out_rows.append(row)
    except KeyboardInterrupt:
        print("writing decisions and exiting...")

    # Write the output csv
    out_header = header
    if not initialized_file:
        out_header += [verified_col]
    with open(outpath, 'w') as fp:
        writer = csv.writer(fp)
        writer.writerow(out_header)
        for row in out_rows:
            writer.writerow(row)
        for row in in_rows[len(out_rows):]:
            if initialized_file:
                writer.writerow(row)
            else:
                writer.writerow(row + [''])

if __name__ == '__main__':
    main()
