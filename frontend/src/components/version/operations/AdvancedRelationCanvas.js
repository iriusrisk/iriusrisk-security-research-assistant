import React, { useState, useEffect, useCallback } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Typography from "@material-ui/core/Typography";
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CardActions from '@material-ui/core/CardActions';
import Button from '@material-ui/core/Button';
import Select from "@material-ui/core/Select";
import FormControl from "@material-ui/core/FormControl";
import InputLabel from "@material-ui/core/InputLabel";
import MenuItem from '@material-ui/core/MenuItem';
import Chip from '@material-ui/core/Chip';
import Avatar from '@material-ui/core/Avatar';
import IconButton from '@material-ui/core/IconButton';
import Tooltip from '@material-ui/core/Tooltip';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import DragIndicatorIcon from '@material-ui/icons/DragIndicator';
import LibraryBooksIcon from '@material-ui/icons/LibraryBooks';
import SecurityIcon from '@material-ui/icons/Security';
import BugReportIcon from '@material-ui/icons/BugReport';
import BuildIcon from '@material-ui/icons/Build';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import ExpandLessIcon from '@material-ui/icons/ExpandLess';
import axios from "axios";
import { failedToast, successToast } from "../../utils/toastFunctions";
import { sortArrayByKey } from "../../utils/commonFunctions";

const useStyles = makeStyles((theme) => ({
    root: {
        display: 'flex',
    },
    container: {
        paddingTop: theme.spacing(4),
        paddingBottom: theme.spacing(4),
    },
    formControl: {
        margin: theme.spacing(1),
        minWidth: 200,
    },
    canvas: {
        minHeight: '800px',
        backgroundColor: '#fafafa',
        padding: theme.spacing(2),
        marginTop: theme.spacing(2),
    },
    libraryContainer: {
        marginBottom: theme.spacing(3),
        border: '2px solid #e0e0e0',
        borderRadius: theme.spacing(1),
        backgroundColor: '#fff',
    },
    libraryHeader: {
        backgroundColor: '#1976d2',
        color: 'white',
        padding: theme.spacing(2),
        borderRadius: `${theme.spacing(1)}px ${theme.spacing(1)}px 0 0`,
    },
    libraryContent: {
        padding: theme.spacing(2),
    },
    riskPatternCard: {
        backgroundColor: '#f3e5f5',
        marginBottom: theme.spacing(2),
        border: '1px solid #ce93d8',
    },
    useCaseCard: {
        backgroundColor: '#e8f5e8',
        marginBottom: theme.spacing(1),
        marginLeft: theme.spacing(2),
        border: '1px solid #a5d6a7',
    },
    threatCard: {
        backgroundColor: '#fff3e0',
        marginBottom: theme.spacing(1),
        marginLeft: theme.spacing(2),
        border: '1px solid #ffcc02',
        position: 'relative',
    },
    weaknessCard: {
        backgroundColor: '#fce4ec',
        marginBottom: theme.spacing(1),
        marginLeft: theme.spacing(2),
        border: '1px solid #f48fb1',
    },
    controlCard: {
        backgroundColor: '#e0f2f1',
        marginBottom: theme.spacing(1),
        marginLeft: theme.spacing(2),
        border: '1px solid #80cbc4',
    },
    draggable: {
        cursor: 'grab',
        '&:active': {
            cursor: 'grabbing',
        },
        '&:hover': {
            boxShadow: theme.shadows[4],
            transform: 'translateY(-2px)',
            transition: 'all 0.2s ease',
        },
    },
    dropZone: {
        minHeight: '60px',
        border: '2px dashed #ccc',
        borderRadius: theme.spacing(1),
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        margin: theme.spacing(1),
        transition: 'all 0.2s ease',
        backgroundColor: '#f9f9f9',
        '&:hover': {
            borderColor: '#2196f3',
            backgroundColor: 'rgba(33, 150, 243, 0.1)',
        },
    },
    dropZoneActive: {
        borderColor: '#2196f3',
        backgroundColor: 'rgba(33, 150, 243, 0.2)',
        transform: 'scale(1.02)',
    },
    itemType: {
        fontSize: '0.75rem',
        color: '#666',
        marginTop: theme.spacing(0.5),
        display: 'flex',
        alignItems: 'center',
        gap: theme.spacing(0.5),
    },
    mitigationChip: {
        marginTop: theme.spacing(1),
    },
    controls: {
        marginBottom: theme.spacing(2),
        display: 'flex',
        gap: theme.spacing(2),
        flexWrap: 'wrap',
    },
    dragHandle: {
        position: 'absolute',
        top: theme.spacing(1),
        right: theme.spacing(1),
        color: '#666',
        cursor: 'grab',
    },
    elementIcon: {
        marginRight: theme.spacing(1),
        fontSize: '1.2rem',
    },
    emptyState: {
        textAlign: 'center',
        padding: theme.spacing(4),
        color: '#666',
    },
    crossLibraryIndicator: {
        position: 'absolute',
        top: -8,
        right: -8,
        backgroundColor: '#ff5722',
        color: 'white',
        borderRadius: '50%',
        width: 24,
        height: 24,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '0.75rem',
        fontWeight: 'bold',
    },
    expandButton: {
        marginLeft: theme.spacing(1),
        padding: theme.spacing(0.5),
        minWidth: 'auto',
        '&:hover': {
            backgroundColor: 'rgba(0, 0, 0, 0.04)',
        },
    },
    collapsibleContent: {
        transition: 'all 0.3s ease',
        overflow: 'hidden',
    },
    collapsed: {
        maxHeight: 0,
        opacity: 0,
    },
    expanded: {
        maxHeight: '2000px',
        opacity: 1,
    },
    headerRow: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
    },
    itemCount: {
        fontSize: '0.75rem',
        color: '#666',
        marginLeft: theme.spacing(1),
    },
}));

// Drag and Drop Item Types
const ItemTypes = {
    USECASE: 'usecase',
    THREAT: 'threat',
    WEAKNESS: 'weakness',
    CONTROL: 'control',
};

// Draggable Component with enhanced visual feedback
const DraggableItem = ({ item, type, children, sourceLibrary }) => {
    const [{ isDragging }, drag] = useDrag({
        type: "CARD",
        item: { type, item, sourceLibrary },
        collect: (monitor) => ({
            isDragging: monitor.isDragging(),
        }),
        canDrag: () => !!(type && item), // Only allow dragging if type and item are defined
    }, [type, item, sourceLibrary]);

    // Safety check to prevent undefined type errors
    if (!type || !item) {
        return <div>{children}</div>;
    }

    return (
        <div
            ref={drag}
            style={{
                opacity: isDragging ? 0.5 : 1,
                cursor: 'grab',
                position: 'relative',
            }}
        >
            {children}
        </div>
    );
};

// Enhanced Drop Zone Component
const DropZone = ({ accept, onDrop, children, className, targetLibrary, sourceLibrary }) => {
    const [{ isOver, canDrop }, drop] = useDrop({
        accept: "CARD",
        drop: (item) => onDrop && onDrop(item),
        canDrop: (item) => {
            // Allow cross-library drops if accept and onDrop are defined
            return !!(accept && onDrop);
        },
        collect: (monitor) => ({
            isOver: monitor.isOver(),
            canDrop: monitor.canDrop(),
        }),
    }, [accept, onDrop]);

    // Safety check to prevent undefined accept errors
    if (!accept || !onDrop) {
        return <div className={className}>{children}</div>;
    }

    const isCrossLibrary = sourceLibrary && targetLibrary && sourceLibrary !== targetLibrary;

    return (
        <div
            ref={drop}
            className={`${className} ${isOver && canDrop ? 'dropZoneActive' : ''}`}
        >
            {isCrossLibrary && (
                <div className="crossLibraryIndicator">
                    <LibraryBooksIcon fontSize="small" />
                </div>
            )}
            {children}
        </div>
    );
};

// Element Icon Component
const ElementIcon = ({ type }) => {
    const classes = useStyles();
    
    switch (type) {
        case 'usecase':
            return <LibraryBooksIcon className={classes.elementIcon} />;
        case 'threat':
            return <SecurityIcon className={classes.elementIcon} />;
        case 'weakness':
            return <BugReportIcon className={classes.elementIcon} />;
        case 'control':
            return <BuildIcon className={classes.elementIcon} />;
        default:
            return <DragIndicatorIcon className={classes.elementIcon} />;
    }
};

const AdvancedRelationCanvas = (props) => {
    const classes = useStyles();
    const { match, version: initialVersion } = props;    
    const [version, setVersion] = useState(initialVersion || (match && match.params.id));
    const [libraries, setLibraries] = useState([]);
    const [selectedLibraries, setSelectedLibraries] = useState([]);
    const [allRelations, setAllRelations] = useState({});
    const [riskPatterns, setRiskPatterns] = useState({});
    const [usecases, setUsecases] = useState([]);
    const [threats, setThreats] = useState([]);
    const [weaknesses, setWeaknesses] = useState([]);
    const [controls, setControls] = useState([]);
    const [loading, setLoading] = useState(false);
    const [expandedItems, setExpandedItems] = useState(new Set());

    const loadLibraries = useCallback(() => {
        if (!version) return;
        axios.get('/api/version/' + version + '/library')
            .then(res => {
                setLibraries(res.data);
            })
            .catch(err => failedToast(err));
    }, [version]);

    const loadVersionData = useCallback(() => {
        if (!version) return;
        setLoading(true);
        Promise.all([
            axios.get('/api/version/' + version + '/usecase'),
            axios.get('/api/version/' + version + '/threat'),
            axios.get('/api/version/' + version + '/weakness'),
            axios.get('/api/version/' + version + '/control'),
        ]).then(([usecasesRes, threatsRes, weaknessesRes, controlsRes]) => {
            setUsecases(sortArrayByKey(usecasesRes.data, "ref"));
            setThreats(sortArrayByKey(threatsRes.data, "ref"));
            setWeaknesses(sortArrayByKey(weaknessesRes.data, "ref"));
            setControls(sortArrayByKey(controlsRes.data, "ref"));
            setLoading(false);
        }).catch(err => {
            failedToast(err);
            setLoading(false);
        });
    }, [version]);

    const loadLibraryData = useCallback(() => {
        if (!version || selectedLibraries.length === 0) return;
        setLoading(true);
        const promises = selectedLibraries.map(library => 
            Promise.all([
                axios.get(`/version/${version}/${library}/riskPattern`),
                axios.get(`/version/${version}/${library}/relation`),
            ]).then(([riskPatternsRes, relationsRes]) => ({
                library,
                riskPatterns: sortArrayByKey(riskPatternsRes.data, "ref"),
                relations: relationsRes.data
            }))
        );

        Promise.all(promises)
            .then(results => {
                const newRiskPatterns = {};
                const newAllRelations = {};
                
                results.forEach(({ library, riskPatterns, relations }) => {
                    newRiskPatterns[library] = riskPatterns;
                    newAllRelations[library] = relations;
                });
                
                setRiskPatterns(newRiskPatterns);
                setAllRelations(newAllRelations);
                setLoading(false);
            })
            .catch(err => {
                failedToast(err);
                setLoading(false);
            });
    }, [version, selectedLibraries]);

    // Load initial data
    useEffect(() => {
        if (version) {
            loadLibraries();
            loadVersionData();
        }
    }, [version, loadLibraries, loadVersionData]);

    // Load data when selected libraries change
    useEffect(() => {
        if (selectedLibraries.length > 0 && version) {
            loadLibraryData();
        }
    }, [selectedLibraries, version, loadLibraryData]);

    // Helper function to get element by UUID
    const getElement = (uuid, elementList) => {
        return elementList.find(el => el.uuid === uuid);
    };

    // Group relations by risk pattern and use case for a specific library
    const groupRelations = (libraryRelations) => {
        const grouped = {};
        
        libraryRelations.forEach(relation => {
            const rpUuid = relation.risk_pattern_uuid;
            const ucUuid = relation.usecase_uuid;
            
            if (!grouped[rpUuid]) {
                grouped[rpUuid] = {};
            }
            if (!grouped[rpUuid][ucUuid]) {
                grouped[rpUuid][ucUuid] = [];
            }
            
            grouped[rpUuid][ucUuid].push(relation);
        });
        
        return grouped;
    };

    // Enhanced handle drop operations with cross-library support
    const handleDrop = useCallback((droppedItem, targetUsecaseUuid, targetRiskPatternUuid, targetLibrary, targetType = 'usecase') => {
        const { type, item, sourceLibrary } = droppedItem;
        
        // Find the source relation
        const sourceRelations = allRelations[sourceLibrary] || [];
        const sourceRelation = sourceRelations.find(r => {
            switch (type) {
                case ItemTypes.USECASE:
                    return r.usecase_uuid === item.uuid;
                case ItemTypes.THREAT:
                    return r.threat_uuid === item.uuid;
                case ItemTypes.WEAKNESS:
                    return r.weakness_uuid === item.uuid;
                case ItemTypes.CONTROL:
                    return r.control_uuid === item.uuid;
                default:
                    return false;
            }
        });

        if (!sourceRelation) {
            failedToast("Source relation not found");
            return;
        }

        // Create new relation with updated target based on target type
        let newRelation;
        if (targetType === 'riskpattern') {
            // Dropping into a risk pattern - create new use case relation
            newRelation = {
                risk_pattern_uuid: targetRiskPatternUuid,
                usecase_uuid: type === ItemTypes.USECASE ? item.uuid : sourceRelation.usecase_uuid,
                threat_uuid: type === ItemTypes.THREAT ? item.uuid : sourceRelation.threat_uuid,
                weakness_uuid: type === ItemTypes.WEAKNESS ? item.uuid : sourceRelation.weakness_uuid,
                control_uuid: type === ItemTypes.CONTROL ? item.uuid : sourceRelation.control_uuid,
                mitigation: sourceRelation.mitigation
            };
        } else if (targetType === 'threat') {
            // Dropping into a threat - update the threat's weakness/control
            newRelation = {
                risk_pattern_uuid: targetRiskPatternUuid,
                usecase_uuid: targetUsecaseUuid,
                threat_uuid: targetRiskPatternUuid, // This is actually the threat UUID
                weakness_uuid: type === ItemTypes.WEAKNESS ? item.uuid : sourceRelation.weakness_uuid,
                control_uuid: type === ItemTypes.CONTROL ? item.uuid : sourceRelation.control_uuid,
                mitigation: sourceRelation.mitigation
            };
        } else if (targetType === 'weakness') {
            // Dropping into a weakness - update the weakness's control
            newRelation = {
                risk_pattern_uuid: targetRiskPatternUuid,
                usecase_uuid: targetUsecaseUuid,
                threat_uuid: targetRiskPatternUuid, // This is actually the threat UUID
                weakness_uuid: targetUsecaseUuid, // This is actually the weakness UUID
                control_uuid: type === ItemTypes.CONTROL ? item.uuid : sourceRelation.control_uuid,
                mitigation: sourceRelation.mitigation
            };
        } else {
            // Default: dropping into a use case
            newRelation = {
                risk_pattern_uuid: targetRiskPatternUuid,
                usecase_uuid: targetUsecaseUuid,
                threat_uuid: type === ItemTypes.THREAT ? item.uuid : sourceRelation.threat_uuid,
                weakness_uuid: type === ItemTypes.WEAKNESS ? item.uuid : sourceRelation.weakness_uuid,
                control_uuid: type === ItemTypes.CONTROL ? item.uuid : sourceRelation.control_uuid,
                mitigation: sourceRelation.mitigation
            };
        }

        // Add new relation to target library
        axios.post(`/version/${version}/${targetLibrary}/relation`, newRelation)
            .then(res => {
                if (res.status === 200 && res.data) {
                    // Handle removal based on type
                    if (type === ItemTypes.USECASE) {
                        // Remove the entire use case branch from source
                        const relationsToRemove = sourceRelations.filter(r => 
                            r.usecase_uuid === item.uuid
                        );
                        
                        if (relationsToRemove.length > 0) {
                            axios.delete(`/version/${version}/${sourceLibrary}/relation`, {
                                data: relationsToRemove
                            }).then(() => {
                                successToast(`Use case moved from ${sourceLibrary} to ${targetLibrary}`);
                                loadLibraryData();
                            }).catch(err => failedToast("Error removing old relations: " + err));
                        }
                    } else if (type === ItemTypes.THREAT) {
                        // Remove the entire threat branch from source
                        const relationsToRemove = sourceRelations.filter(r => 
                            r.threat_uuid === item.uuid
                        );
                        
                        if (relationsToRemove.length > 0) {
                            axios.delete(`/version/${version}/${sourceLibrary}/relation`, {
                                data: relationsToRemove
                            }).then(() => {
                                successToast(`Threat moved from ${sourceLibrary} to ${targetLibrary}`);
                                loadLibraryData();
                            }).catch(err => failedToast("Error removing old relations: " + err));
                        }
                    } else {
                        // For weakness and control, update the relation
                        const updatedRelation = {
                            ...sourceRelation,
                            risk_pattern_uuid: targetRiskPatternUuid,
                            usecase_uuid: targetUsecaseUuid
                        };
                        
                        axios.put(`/version/${version}/${sourceLibrary}/relation`, updatedRelation)
                            .then(() => {
                                successToast(`${type} moved from ${sourceLibrary} to ${targetLibrary}`);
                                loadLibraryData();
                            }).catch(err => failedToast("Error updating relation: " + err));
                    }
                }
            })
            .catch(err => failedToast("Error creating new relation: " + err));
    }, [allRelations, version, loadLibraryData]);

    // Toggle expanded state for items
    const toggleExpanded = useCallback((itemId) => {
        setExpandedItems(prev => {
            const newSet = new Set(prev);
            if (newSet.has(itemId)) {
                newSet.delete(itemId);
            } else {
                newSet.add(itemId);
            }
            return newSet;
        });
    }, []);

    // Check if item is expanded
    const isExpanded = useCallback((itemId) => {
        return expandedItems.has(itemId);
    }, [expandedItems]);

    const renderRelationTree = (library) => {
        const libraryRelations = allRelations[library] || [];
        const libraryRiskPatterns = riskPatterns[library] || [];
        const grouped = groupRelations(libraryRelations);
        
        if (Object.keys(grouped).length === 0) {
            return (
                <div className={classes.emptyState}>
                    <Typography variant="h6" color="textSecondary">
                        No relations found in this library
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                        Add relations using the Manage Relations tab
                    </Typography>
                </div>
            );
        }
        
        return Object.keys(grouped).map(rpUuid => {
            const riskPattern = getElement(rpUuid, libraryRiskPatterns);
            if (!riskPattern) return null;

            const useCaseCount = Object.keys(grouped[rpUuid]).length;
            const riskPatternId = `riskpattern-${library}-${rpUuid}`;
            const isRiskPatternExpanded = isExpanded(riskPatternId);

            return (
                <div key={rpUuid} className={classes.librarySection}>
                    <Card className={classes.riskPatternCard}>
                        <CardContent>
                            <div className={classes.headerRow}>
                                <Typography variant="h6">
                                    <LibraryBooksIcon className={classes.elementIcon} />
                                    Risk Pattern: {riskPattern.ref} - {riskPattern.name}
                                    <span className={classes.itemCount}>({useCaseCount} use cases)</span>
                                </Typography>
                                <Button
                                    size="small"
                                    onClick={() => toggleExpanded(riskPatternId)}
                                    className={classes.expandButton}
                                >
                                    {isRiskPatternExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                                </Button>
                            </div>
                            
                            <div className={`${classes.collapsibleContent} ${isRiskPatternExpanded ? classes.expanded : classes.collapsed}`}>
                                <DropZone
                                    accept={[ItemTypes.USECASE, ItemTypes.THREAT, ItemTypes.WEAKNESS, ItemTypes.CONTROL]}
                                    onDrop={(item) => handleDrop(item, null, rpUuid, library, 'riskpattern')}
                                    className={classes.dropZone}
                                    targetLibrary={library}
                                >
                                    <Typography variant="body2" color="textSecondary">
                                        Drop use cases here to move them to this risk pattern
                                    </Typography>
                                </DropZone>
                                
                                {Object.keys(grouped[rpUuid]).map(ucUuid => {
                                    const usecase = getElement(ucUuid, usecases);
                                    if (!usecase) return null;

                                    const threatCount = grouped[rpUuid][ucUuid].length;
                                    const useCaseId = `usecase-${library}-${ucUuid}`;
                                    const isUseCaseExpanded = isExpanded(useCaseId);

                                    return (
                                        <div key={ucUuid} className={classes.librarySection}>
                                            <DraggableItem item={usecase} type={ItemTypes.USECASE} sourceLibrary={library}>
                                                <Card className={classes.useCaseCard}>
                                                    <CardContent>
                                                        <div className={classes.headerRow}>
                                                            <Typography variant="subtitle1">
                                                                <ElementIcon type="usecase" />
                                                                Use Case: {usecase.ref} - {usecase.name}
                                                                <span className={classes.itemCount}>({threatCount} threats)</span>
                                                            </Typography>
                                                            <Button
                                                                size="small"
                                                                onClick={() => toggleExpanded(useCaseId)}
                                                                className={classes.expandButton}
                                                            >
                                                                {isUseCaseExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                                                            </Button>
                                                        </div>
                                                        <Typography className={classes.itemType}>
                                                            <DragIndicatorIcon fontSize="small" />
                                                            Drag to move entire use case branch
                                                        </Typography>
                                                        
                                                        <div className={`${classes.collapsibleContent} ${isUseCaseExpanded ? classes.expanded : classes.collapsed}`}>
                                                            <DropZone
                                                                accept={[ItemTypes.THREAT, ItemTypes.WEAKNESS, ItemTypes.CONTROL]}
                                                                onDrop={(item) => handleDrop(item, ucUuid, rpUuid, library, 'usecase')}
                                                                className={classes.dropZone}
                                                                targetLibrary={library}
                                                            >
                                                                <Typography variant="body2" color="textSecondary">
                                                                    Drop items here to move them to this use case
                                                                </Typography>
                                                            </DropZone>

                                                            {grouped[rpUuid][ucUuid].map(relation => {
                                                                const threat = getElement(relation.threat_uuid, threats);
                                                                if (!threat) return null;

                                                                const hasWeakness = !!relation.weakness_uuid;
                                                                const hasControl = !!relation.control_uuid;
                                                                const threatId = `threat-${library}-${threat.uuid}`;
                                                                const isThreatExpanded = isExpanded(threatId);

                                                                return (
                                                                    <div key={relation.uuid}>
                                                                        <DraggableItem item={threat} type={ItemTypes.THREAT} sourceLibrary={library}>
                                                                            <Card className={classes.threatCard}>
                                                                                <CardContent>
                                                                                    <div className={classes.headerRow}>
                                                                                        <Typography variant="body2">
                                                                                            <ElementIcon type="threat" />
                                                                                            Threat: {threat.ref} - {threat.name}
                                                                                            {(hasWeakness || hasControl) && (
                                                                                                <span className={classes.itemCount}>
                                                                                                    ({hasWeakness ? '1 weakness' : ''}{hasWeakness && hasControl ? ', ' : ''}{hasControl ? '1 control' : ''})
                                                                                                </span>
                                                                                            )}
                                                                                        </Typography>
                                                                                        {(hasWeakness || hasControl) && (
                                                                                            <Button
                                                                                                size="small"
                                                                                                onClick={() => toggleExpanded(threatId)}
                                                                                                className={classes.expandButton}
                                                                                            >
                                                                                                {isThreatExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                                                                                            </Button>
                                                                                        )}
                                                                                    </div>
                                                                                    <Typography className={classes.itemType}>
                                                                                        <DragIndicatorIcon fontSize="small" />
                                                                                        Drag to move entire threat branch
                                                                                    </Typography>
                                                                                    
                                                                                    <div className={`${classes.collapsibleContent} ${isThreatExpanded ? classes.expanded : classes.collapsed}`}>
                                                                                        <DropZone
                                                                                            accept={[ItemTypes.WEAKNESS, ItemTypes.CONTROL]}
                                                                                            onDrop={(item) => handleDrop(item, ucUuid, threat.uuid, library, 'threat')}
                                                                                            className={classes.dropZone}
                                                                                            targetLibrary={library}
                                                                                        >
                                                                                            <Typography variant="body2" color="textSecondary">
                                                                                                Drop weaknesses/controls here
                                                                                            </Typography>
                                                                                        </DropZone>
                                                                                        
                                                                                        {relation.weakness_uuid && (
                                                                                            <div>
                                                                                                {(() => {
                                                                                                    const weakness = getElement(relation.weakness_uuid, weaknesses);
                                                                                                    if (!weakness) return null;
                                                                                                    
                                                                                                    return (
                                                                                                        <DraggableItem item={weakness} type={ItemTypes.WEAKNESS} sourceLibrary={library}>
                                                                                                            <Card className={classes.weaknessCard}>
                                                                                                                <CardContent>
                                                                                                                    <div className={classes.headerRow}>
                                                                                                                        <Typography variant="body2">
                                                                                                                            <ElementIcon type="weakness" />
                                                                                                                            Weakness: {weakness.ref} - {weakness.name}
                                                                                                                            {hasControl && <span className={classes.itemCount}>(1 control)</span>}
                                                                                                                        </Typography>
                                                                                                                        {hasControl && (
                                                                                                                            <Button
                                                                                                                                size="small"
                                                                                                                                onClick={() => toggleExpanded(`weakness-${library}-${weakness.uuid}`)}
                                                                                                                                className={classes.expandButton}
                                                                                                                            >
                                                                                                                                {isExpanded(`weakness-${library}-${weakness.uuid}`) ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                                                                                                                            </Button>
                                                                                                                        )}
                                                                                                                    </div>
                                                                                                                    <Typography className={classes.itemType}>
                                                                                                                        <DragIndicatorIcon fontSize="small" />
                                                                                                                        Drag to move weakness
                                                                                                                    </Typography>
                                                                                                                    
                                                                                                                    <div className={`${classes.collapsibleContent} ${isExpanded(`weakness-${library}-${weakness.uuid}`) ? classes.expanded : classes.collapsed}`}>
                                                                                                                        <DropZone
                                                                                                                            accept={[ItemTypes.CONTROL]}
                                                                                                                            onDrop={(item) => handleDrop(item, ucUuid, threat.uuid, library, 'weakness')}
                                                                                                                            className={classes.dropZone}
                                                                                                                            targetLibrary={library}
                                                                                                                        >
                                                                                                                            <Typography variant="body2" color="textSecondary">
                                                                                                                                Drop controls here
                                                                                                                            </Typography>
                                                                                                                        </DropZone>
                                                                                                                        
                                                                                                                        {relation.control_uuid && (
                                                                                                                            <div>
                                                                                                                                {(() => {
                                                                                                                                    const control = getElement(relation.control_uuid, controls);
                                                                                                                                    if (!control) return null;
                                                                                                    
                                                                                                                                    return (
                                                                                                                                        <DraggableItem item={control} type={ItemTypes.CONTROL} sourceLibrary={library}>
                                                                                                                                            <Card className={classes.controlCard}>
                                                                                                                                                <CardContent>
                                                                                                                                                    <Typography variant="body2">
                                                                                                                                                        <ElementIcon type="control" />
                                                                                                                                                        Control: {control.ref} - {control.name}
                                                                                                                                                    </Typography>
                                                                                                                                                    <Typography className={classes.itemType}>
                                                                                                                                                        <DragIndicatorIcon fontSize="small" />
                                                                                                                                                        Drag to move control
                                                                                                                                                    </Typography>
                                                                                                                                                    <Chip
                                                                                                                                                        label={`Mitigation: ${relation.mitigation}%`}
                                                                                                                                                        className={classes.mitigationChip}
                                                                                                                                                        color="primary"
                                                                                                                                                        size="small"
                                                                                                                                                    />
                                                                                                                                                </CardContent>
                                                                                                                                            </Card>
                                                                                                                                        </DraggableItem>
                                                                                                                                    );
                                                                                                                                })()}
                                                                                                                            </div>
                                                                                                                        )}
                                                                                                                    </div>
                                                                                                                </CardContent>
                                                                                                            </Card>
                                                                                                        </DraggableItem>
                                                                                                    );
                                                                                                })()}
                                                                                            </div>
                                                                                        )}
                                                                                    </div>
                                                                                </CardContent>
                                                                            </Card>
                                                                        </DraggableItem>
                                                                    </div>
                                                                );
                                                            })}
                                                        </div>
                                                    </CardContent>
                                                </Card>
                                            </DraggableItem>
                                        </div>
                                    );
                                })}
                            </div>
                        </CardContent>
                    </Card>
                </div>
            );
        });
    };

    return (
        <DndProvider backend={HTML5Backend}>
            <div className={classes.root}>
                <CssBaseline />
                <Container maxWidth="xl" className={classes.container}>
                    <Typography variant="h4" gutterBottom>
                        Advanced Relation Drag & Drop Canvas
                    </Typography>
                    
                    <div className={classes.controls}>
                        <FormControl className={classes.formControl}>
                            <InputLabel>Select Libraries</InputLabel>
                            <Select
                                multiple
                                value={selectedLibraries}
                                onChange={(event) => setSelectedLibraries(event.target.value)}
                                renderValue={(selected) => (
                                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                                        {selected.map((value) => (
                                            <Chip key={value} label={value} size="small" />
                                        ))}
                                    </div>
                                )}
                            >
                                {libraries.map((library, index) => (
                                    <MenuItem key={index} value={library}>
                                        {library}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                        
                        <Button 
                            variant="outlined" 
                            onClick={loadLibraryData}
                            disabled={loading}
                        >
                            {loading ? 'Loading...' : 'Refresh'}
                        </Button>
                    </div>

                    {loading && (
                        <div style={{ textAlign: 'center', padding: '20px' }}>
                            <Typography variant="h6">Loading...</Typography>
                        </div>
                    )}
                    
                    {!loading && selectedLibraries.length > 0 && (
                        <Grid container spacing={2}>
                            {selectedLibraries.map(library => (
                                <Grid item xs={12} md={6} key={library}>
                                    <div className={classes.libraryContainer}>
                                        <div className={classes.libraryHeader}>
                                            <Typography variant="h6">
                                                <LibraryBooksIcon className={classes.elementIcon} />
                                                Library: {library}
                                            </Typography>
                                        </div>
                                        <div className={classes.libraryContent}>
                                            {renderRelationTree(library)}
                                        </div>
                                    </div>
                                </Grid>
                            ))}
                        </Grid>
                    )}
                </Container>
            </div>
        </DndProvider>
    );
};

export default AdvancedRelationCanvas;
