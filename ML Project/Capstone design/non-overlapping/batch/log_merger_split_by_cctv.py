first_1 = str(19216800000204)
first_2 = str(19216800000205)
second_1 = str(19216800000202)
second_2 = str(19216800000203)
third_1 = str(19216800000200)
third_2 = str(19216800000201)


# cctv_1 and cctv_2 is connected - first

f1 = open("logs/logmerger/1111/500_2/all/first_cctv1.tsv", "wt")
f2 = open("logs/logmerger/1111/500_2/all/first_cctv2.tsv", "wt")

s1 = open("logs/logmerger/1111/500_2/all/second_cctv1.tsv", "wt")
s2 = open("logs/logmerger/1111/500_2/all/second_cctv2.tsv", "wt")

th1 = open("logs/logmerger/1111/500_2/all/third_cctv1.tsv", "wt")
th2 = open("logs/logmerger/1111/500_2/all/third_cctv2.tsv", "wt")

with open('logs/logmerger/1111/500_2/all/output.tsv', 'r') as out:
    lines = out.readlines()

    for line in lines:
        segmented = line.split('\t')

        # segmented[1] == 1: human
        # segmented[1] == 2: vehicle
        # segmented[1] == 100: head

        if segmented[1] == '1':
            new_line = [
                segmented[0], # object_id
                segmented[2], # cctv_id
                segmented[3], # timestamp
                segmented[4], # grid_list
                #############
                segmented[5], # avg_size_grid
                segmented[6], # std_size_grid
                segmented[9], # avg_speed_grid
                segmented[10], # std_speed_grid
                #############
            ]

            line = '\t'.join(new_line) + '\n'

            # print('entry_color', segmented[12])
            # print('exit_color', segmented[22])

            if segmented[2] == first_1:
                f1.write(line)
            elif segmented[2] == first_2:
                f2.write(line)
            elif segmented[2] == second_1:
                s1.write(line)
            elif segmented[2] == second_2:
                s2.write(line)
            elif segmented[2] == third_1:
                th1.write(line)
            elif segmented[2] == third_2:
                th2.write(line)
