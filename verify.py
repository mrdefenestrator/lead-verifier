#!/usr/bin/env python3
import csv
import sys
import webbrowser
import sys
import tty
import termios


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def prompt_rec(prompt: str, options=('y','n')):
    """Prompt for a single character of input and return the value once entered
    """
    sys.stdout.write(f"{prompt} ({'/'.join(options)}): ")
    value = getch()
    sys.stdout.write(f"{value}\n")

    if value not in options:
        return prompt_rec(prompt, options)

    return value


def read_csv(file_path):
    rows = []
    with open(file_path, 'r') as fp:
        reader = csv.reader(fp)
        header = reader.__next__()

        for row in reader:
            rows.append(row)
    return header, rows


def write_csv(file_path, out_header, out_rows):
    with open(file_path, 'w') as fp:
        writer = csv.writer(fp)
        writer.writerow(out_header)
        for row in out_rows:
            writer.writerow(row)


def main():
    if len(sys.argv) < 2:
        print("please give the path of the csv file to verify")
        sys.exit(1)

    file_path = sys.argv[1]

    in_header, in_rows = read_csv(file_path)

    verified_col_name = 'verified'
    initialized_file = False
    if in_header[-1] == verified_col_name:
        # file previously used for verification
        initialized_file = True

    # discover the url column offset
    url_offset = in_header.index("URL")

    try:
        # Make a decision on each of the rows
        verified_urls = set()
        not_verified_urls = set()
        out_rows = []
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
                print("\n", row)
                webbrowser.open(f"http://{url}", new=0, autoraise=True)
                response = prompt_rec("Is this relevant?", ('y', 'n', 'x'))
                if response == 'x':
                    print(f"\nsaving decisions and exiting...")
                    break
                verified = response == 'y'

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
        print(f"\nsaving decisions and exiting...")

    # generate the output header
    out_header = in_header
    if not initialized_file:
        out_header += [verified_col_name]

    # buffer the output rows with those not yet processed
    verified_count = len(out_rows)
    for row in in_rows[verified_count:]:
        if initialized_file:
            out_rows.append(row)
        else:
            out_rows.append(row + [''])

    write_csv(file_path, out_header, out_rows)


if __name__ == '__main__':
    main()
