import axios from "axios";

// Element type configurations
export const ELEMENT_TYPES = {
    "Use case": {
        createEndpoint: (version) => `/version/${version}/usecase`,
        updateEndpoint: (version) => `/version/${version}/usecase`,
        createRequest: (data) => ({
            ref: data.ref,
            name: data.name,
            desc: data.desc
        }),
        updateRequest: (element) => element,
        fields: ['basic']
    },
    "Threat": {
        createEndpoint: (version) => `/version/${version}/threat`,
        updateEndpoint: (version) => `/version/${version}/threat`,
        createRequest: (data) => ({
            ref: data.ref,
            name: data.name,
            desc: data.desc,
            risk_rating: {
                confidentiality: data.riskRating.confidentiality,
                integrity: data.riskRating.integrity,
                availability: data.riskRating.availability,
                ease_of_exploitation: data.riskRating.ease_of_exploitation
            },
            scope: data.scope || [],
            stride: data.stride || []
        }),
        updateRequest: (element) => element,
        fields: ['basic', 'riskRating', 'scope', 'stride', 'references']
    },
    "Weakness": {
        createEndpoint: (version) => `/version/${version}/weakness`,
        updateEndpoint: (version) => `/version/${version}/weakness`,
        createRequest: (data) => ({
            ref: data.ref,
            name: data.name,
            desc: data.desc,
            impact: data.impact,
            steps: data.test.steps
        }),
        updateRequest: (data) => ({
            uuid: data.uuid,
            ref: data.ref,
            name: data.name,
            desc: data.desc,
            impact: data.impact,
            steps: data.test.steps
        }),
        fields: ['basic', 'impact', 'test']
    },
    "Control": {
        createEndpoint: (version) => `/version/${version}/control`,
        updateEndpoint: (version) => `/version/${version}/control`,
        createRequest: (data) => ({
            ref: data.ref,
            name: data.name,
            desc: data.desc,
            state: data.state,
            cost: data.cost,
            steps: data.test.steps
        }),
        updateRequest: (element) => element,
        fields: ['basic', 'state', 'cost', 'standards', 'references', 'test']
    }
};

/**
 * Creates an element with proper error handling and two-step process
 * @param {string} elementType - The type of element to create
 * @param {string} version - The version to create the element in
 * @param {object} data - The element data
 * @returns {Promise<object>} The created element
 */
export const createElementWithUpdate = async (elementType, version, data) => {
    const config = ELEMENT_TYPES[elementType];
    if (!config) {
        throw new Error("Invalid element type");
    }

    try {
        // Step 1: Create the element with basic data
        const createResponse = await axios.post(
            config.createEndpoint(version), 
            config.createRequest(data)
        );
        
        const createdElement = createResponse.data;
        
        // Step 2: Update with additional data if needed
        if (data.references.length > 0 || data.standards.length > 0 || data.test.references.length > 0) {
            // Prepare full element data for update
            const updateData = {
                ...createdElement,
                references: data.references,
                standards: data.standards,
                test: {
                    ...createdElement.test,
                    references: data.test.references
                }
            };
            
            await axios.put(
                config.updateEndpoint(version),
                updateData
            );
        }
        
        return createdElement;
    } catch (error) {
        throw error;
    }
};

/**
 * Validates element data before creation
 * @param {string} elementType - The type of element
 * @param {object} data - The element data
 * @returns {object} Validation result with isValid boolean and errors array
 */
export const validateElementData = (elementType, data) => {
    const errors = [];
    
    // Basic validation for all elements
    if (!data.ref || data.ref.trim() === '') {
        errors.push('Reference is required');
    }
    if (!data.name || data.name.trim() === '') {
        errors.push('Name is required');
    }
    if (!data.desc || data.desc.trim() === '') {
        errors.push('Description is required');
    }
    
    // Element-specific validation
    const config = ELEMENT_TYPES[elementType];
    if (config) {
        if (config.fields.includes('riskRating')) {
            const riskRating = data.riskRating;
            if (!riskRating.confidentiality || !riskRating.integrity || 
                !riskRating.availability || !riskRating.ease_of_exploitation) {
                errors.push('All risk rating fields are required for threats');
            }
        }
        
        if (config.fields.includes('impact') && (!data.impact || data.impact.trim() === '')) {
            errors.push('Impact is required for weaknesses');
        }
        
        if (config.fields.includes('state') && (!data.state || data.state.trim() === '')) {
            errors.push('State is required for controls');
        }
        
        if (config.fields.includes('cost') && (!data.cost || data.cost.trim() === '')) {
            errors.push('Cost is required for controls');
        }
    }
    
    return {
        isValid: errors.length === 0,
        errors
    };
};

/**
 * Gets the default form data for an element type
 * @param {string} elementType - The type of element
 * @returns {object} Default form data
 */
export const getDefaultFormData = (elementType) => {
    return {
        ref: "",
        name: "",
        desc: "",
        state: "",
        cost: "",
        impact: "",
        riskRating: {
            confidentiality: "",
            integrity: "",
            availability: "",
            ease_of_exploitation: "",
        },
        references: [],
        standards: [],
        test: {
            steps: "",
            result: "",
            timestamp: "",
            references: []
        },
    };
};

/**
 * Extracts form data from a form event
 * @param {Event} event - The form submit event
 * @param {object} formData - Current form data state
 * @returns {object} Extracted form data
 */
export const extractFormData = (event, formData) => {
    const form = event.target;
    return {
        ...formData,
        ref: form.ref.value,
        name: form.name.value,
        desc: formData.desc,
        state: form.state?.value || formData.state,
        cost: form.cost?.value || formData.cost,
        impact: form.impact?.value || formData.impact,
        riskRating: {
            confidentiality: form.confidentiality?.value || formData.riskRating.confidentiality,
            integrity: form.integrity?.value || formData.riskRating.integrity,
            availability: form.availability?.value || formData.riskRating.availability,
            ease_of_exploitation: form.ease_of_exploitation?.value || formData.riskRating.ease_of_exploitation,
        },
        scope: formData.scope || [],
        stride: formData.stride || []
    };
}; 