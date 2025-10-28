import Button from "@material-ui/core/Button";
import withStyles from "@material-ui/core/styles/withStyles";
import green from "@material-ui/core/colors/green";

export const excelDelimiter = ",";

export const sortArrayByKey = (array, key) => {
    return array.sort(function(a, b) {
        if (a[key] > b[key]) {
            return 1;
        }
        if (a[key] < b[key]) {
            return -1;
        }
        return 0;
    })
};

export const sortStringArrayInsensitiveCase = (array) => {
    return array.sort((a, b) => a.localeCompare(b, undefined, {sensitivity: 'base'}));
}

export const groupBy = (list, keyGetter) => {
    const map = new Map();
    list.forEach((item) => {
        const key = keyGetter(item);
        const collection = map.get(key);
        if (!collection) {
            map.set(key, [item]);
        } else {
            collection.push(item);
        }
    });
    return map;
}

export const GreenButton = withStyles((theme) => ({
    root: {
        color: theme.palette.getContrastText(green[500]),
        backgroundColor: green[500],
        '&:hover': {
            backgroundColor: green[700],
        },
    },
}))(Button);