# coding=utf-8
# Small python script to show how the graphing algorithm works
# Not used in the primary project itself
import datetime as dt
import sys

import secretsanta
import secretsanta.secretsanta as ss

# CSV column mappings 
FAM_MEMBER_COL = 0
FAM_FAMILY_COL = 1

CONN_SOURCE_COL = 0
CONN_TARGET_COL = 1
CONN_YEAR_COL = 2


def load_family_members(csv_path):
    """
    Returns families_members, a map of families_to_members to their
    associated families_members, and families_to_members, a map of
    families_members to a set of its families_to_members.
    """
    with open(csv_path, "r") as file:
        families_to_members = {}
        members_to_families = {}

        for line in file:
            data = line.strip().split(",")
            member = data[FAM_MEMBER_COL]
            family = data[FAM_FAMILY_COL]

            families_to_members[member] = family
            if family not in members_to_families:
                members_to_families[family] = set()
            members_to_families[family].add(member)

    return families_to_members, members_to_families


def load_connections(csv_path, families, members):
    with open(csv_path, "r") as file:
        connections = secretsanta.ConnectionGraph.ConnectionGraph(families, members)

        for line in file:
            data = line.strip().split(',')
            source = data[CONN_SOURCE_COL]
            target = data[CONN_TARGET_COL]
            year = data[CONN_YEAR_COL]

            connections.add(source, target, year)

    return connections


def save_connections(csv_path, connections):
    with open(csv_path, "w") as file:
        file.write("giver,receiver,year,weight\n")

        for conn in connections:
            file.write(",".join([
                conn.source,
                conn.target,
                str(conn.year),
                str(conn.weight)
            ]) + "\n")


def main():
    argc = len(sys.argv)
    if argc != 4 and argc != 5:
        print("usage: ss.py <familyFile> <old_conn_file> " +
              "<new_conn_file> [<conn_year>]")
        exit(1)

    family_file = sys.argv[1]
    old_conn_file = sys.argv[2]
    new_conn_file = sys.argv[3]
    conn_year = int(sys.argv[4]) if argc == 5 else dt.datetime.now().year

    families_to_members, members_to_families = load_family_members(family_file)
    old_connections = load_connections(old_conn_file,
                                       families_to_members,
                                       members_to_families)

    santa = ss.SecretSanta(families_to_members, members_to_families, old_connections)

    new_connections = santa.generate_connections(conn_year)

    total_weight = sum(conn.weight for conn in new_connections)
    print("Generated new connections for %d with total weight %d"
          % (conn_year, total_weight))

    save_connections(new_conn_file, new_connections)


if __name__ == "__main__":
    main()
