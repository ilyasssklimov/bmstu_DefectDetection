#include "parser.h"
#include <stdlib.h>
#include <errno.h>


inline error_code allocate_predicate(predicate *pred, int count_cmp)
{
    if (pred == NULL)
        return ALLOCATE_ERROR;

    pred->compare = NULL;
    pred->numbers = NULL;
    pred->logic = NULL;

    if (count_cmp <= 0)
        return ALLOCATE_ERROR;

    pred->compare = calloc(count_cmp, sizeof(cmp_opr));
    if (pred->compare == NULL)
	    return ALLOCATE_ERROR;

    pred->numbers = calloc(count_cmp, sizeof(int));
    if (pred->numbers == NULL)
    {
        free(pred->compare);
        pred->compare = NULL;
	    return ALLOCATE_ERROR;
    }

    pred->logic = calloc(count_cmp - 1, sizeof(logic_opr));
    if (pred->logic == NULL)
    {
        free(pred->numbers);
        pred->numbers = NULL;
        free(pred->compare);
        pred->compare = NULL;
	    return ALLOCATE_ERROR;
    }

    pred->count_cmp = count_cmp;
    return OK;
}


inline void free_predicate(predicate **pred)
{
    if (*pred)
    {
        if ((*pred)->compare)
        {
            free((*pred)->compare);
            (*pred)->compare = NULL;
        }
        if ((*pred)->numbers)
        {
            free((*pred)->numbers);
            (*pred)->numbers = NULL;
        }
        if ((*pred)->logic)
        {
            free((*pred)->logic);
            (*pred)->logic = NULL;
        }
        free(*pred);
        *pred = NULL;
    }
}


inline error_code parse_predicate(my_string str_pred, predicate *pred)
{
    error_code find_code = WAIT;

	// разбить предикат на скобки
    int brackets[MAX_BRACKETS];
    int ind = 0;
    int len = length_string(str_pred);
    int left, right;

    my_string tmp_pred = calloc(len + 1, sizeof(char));
	if (tmp_pred == NULL)
	    return ALLOCATE_ERROR;
	copy_string(&tmp_pred, str_pred, len);

    while (find_code == WAIT && ind < MAX_BRACKETS - 1)
    {
        left = find_last_chr(tmp_pred, '(');
        right = find_chr_from(tmp_pred, ')', left);

        if ((left == NOT_FOUND && right == NOT_FOUND) || is_empty(tmp_pred))
        {
            find_code = OK;
        }
        else if (left == NOT_FOUND || right == NOT_FOUND)
        {
            find_code = INVALID_SYNTAX;
        }
        else
        {
            brackets[ind++] = left + 1;
            brackets[ind++] = right;
            erase_string(&tmp_pred, left, right);
        }
    }

    if (find_code == INVALID_SYNTAX || (find_code == WAIT && ind >= MAX_BRACKETS - 1))
	{
        free(tmp_pred);
        return INVALID_SYNTAX;
    }

    // получить логические операторы
    logic_opr logic[MAX_BRACKETS / 2];
    int logic_ind = 0;
	logic_opr res_opr;
	int space_ind;

	my_string str_opr = calloc(3, sizeof(char));
	if (str_opr == NULL)
	{
	    free(tmp_pred);
	    return ALLOCATE_ERROR;
	}

	find_code = WAIT;

	while (find_code == WAIT)
	{
		space_ind = -1;
		while (tmp_pred[++space_ind] == ' ') {}

		erase_string(&tmp_pred, 0, space_ind - 1);

		if (is_empty(tmp_pred))
		{
			find_code = OK;
		}
		else if (length_string(tmp_pred) == 1)
		{
			find_code = INVALID_SYNTAX;
		}
		else
		{
			slice_string(tmp_pred, &str_opr, 0, 2);
			res_opr = get_logic(str_opr);
			if (res_opr == ERROR)
			{
				find_code = INVALID_SYNTAX;
			}
			else
			{
				logic[logic_ind++] = res_opr;
				erase_string(&tmp_pred, 0, 2);
			}
		}
	}

	free(tmp_pred);

    if (find_code == INVALID_SYNTAX)
    {
        free(str_opr);
        return find_code;
    }

    // получить функции с числами
    int numbers[MAX_BRACKETS / 2];
    cmp_opr operators[MAX_BRACKETS / 2];
    cmp_opr tmp_operator;
    int num;
    int opr_ind = 0;
    char *tmp;
    int first_space, second_space;

    my_string expression = calloc(20, sizeof(char));
	if (expression == NULL)
	{
	    free(str_opr);
	    return ALLOCATE_ERROR;
	}

    for (int i = 0; i < ind && find_code == OK; i += 2)
    {
        slice_string(str_pred, &expression, brackets[i], brackets[i + 1]);
        first_space = find_first_chr(expression, ' ');
        second_space = find_last_chr(expression, ' ');

        if (first_space == NOT_FOUND || second_space == NOT_FOUND|| first_space == second_space)
        {
            find_code = INVALID_SYNTAX;
        }
        else
        {
            slice_string(expression, &str_opr, first_space + 1, second_space);
            tmp_operator = get_compare(str_opr);

            erase_string(&expression, 0, second_space);
            errno = 0;
            num = strtol(expression, &tmp, 0);

            if (tmp_operator && *tmp == '\0' && errno == 0)
            {
                operators[opr_ind] = tmp_operator;
                numbers[opr_ind] = num;
                opr_ind++;
            }
            else
            {
                find_code = INVALID_SYNTAX;
            }
        }
    }

	free(str_opr);
	free(expression);

    if (find_code == INVALID_SYNTAX)
        return find_code;

	// выделить память под структуру предиката
    find_code = allocate_predicate(pred, opr_ind);
    if (find_code == ALLOCATE_ERROR)
        return find_code;

    // проинициализировать значения предиката
    for (int i = 0; i < opr_ind; i++)
    {
        pred->compare[i] = operators[opr_ind - i - 1];
        pred->numbers[i] = numbers[opr_ind - i - 1];
    }
    for (int i = 0; i < logic_ind; i++)
    {
        pred->logic[i] = logic[i];
    }

    return find_code;
}


bool do_predicate(predicate *pred, int number)
{
    if (pred == NULL)
        return false;

    bool tmp_result[MAX_BRACKETS / 2];
    for (int i = 0; i < pred->count_cmp; i++)
    {
        tmp_result[i] = pred->compare[i](number, pred->numbers[i]);
    }

    bool total_result = tmp_result[0];

    for (int i = 0; i < pred->count_cmp - 1; i++)
    {
        if (pred->logic[i] == AND)
        {
            total_result = total_result && tmp_result[i + 1];
        }
        else if (pred->logic[i] == OR)
        {
            total_result = total_result || tmp_result[i + 1];
        }
    }

    return total_result;
}