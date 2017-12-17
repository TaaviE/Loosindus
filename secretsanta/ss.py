import datetime as dt
import sys

import secretsanta as ss

# CSV column mappings 
FAM_MEMBER_COL = 0
FAM_FAMILY_COL = 1

CONN_SOURCE_COL = 0
CONN_TARGET_COL = 1
CONN_YEAR_COL = 2


def loadFamilyMembers(csvPath):
    '''
    Returns families, a map of members to their
    associated families, and members, a map of 
    families to a set of its members.
    '''
    with open(csvPath, 'r') as file:

        families = {}
        members = {}

        for line in file:
            data = line.strip().split(',')
            member = data[FAM_MEMBER_COL]
            family = data[FAM_FAMILY_COL]

            families[member] = family
            if family not in members:
                members[family] = set()
            members[family].add(member)

    return families, members


def loadConnections(csvPath, families, members):
    with open(csvPath, 'r') as file:
        connections = ss.ConnectionGraph(families,
                                         members)

        for line in file:
            data = line.strip().split(',')
            source = data[CONN_SOURCE_COL]
            target = data[CONN_TARGET_COL]
            year = data[CONN_YEAR_COL]

            connections.add(source, target, year)

    return connections


def saveConnections(csvPath, connections):
    with open(csvPath, 'w') as file:
        file.write('giver,receiver,year,weight\n')

        for conn in connections:
            file.write(','.join([
                conn.source,
                conn.target,
                str(conn.year),
                str(conn.weight)
            ]) + '\n')


def main():
    argc = len(sys.argv)
    if argc != 4 and argc != 5:
        print('usage: ss.py <familyFile> <oldConnFile> ' +
              '<newConnFile> [<connYear>]')
        exit(1)

    familyFile = sys.argv[1]
    oldConnFile = sys.argv[2]
    newConnFile = sys.argv[3]
    connYear = int(sys.argv[4]) if argc == 5 else dt.datetime.now().year

    families, members = loadFamilyMembers(familyFile)
    oldConnections = loadConnections(oldConnFile,
                                     families,
                                     members)

    santa = ss.SecretSanta(families, members, oldConnections)

    newConnections = santa.genConnections(connYear)

    totalWeight = sum(conn.weight for conn in newConnections)
    print('Generated new connections for %d with total weight %d'
          % (connYear, totalWeight))

    saveConnections(newConnFile, newConnections)


if __name__ == '__main__':
    main()
