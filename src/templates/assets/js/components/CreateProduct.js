import React, {useState} from 'react';
import TagsInput from 'react-tagsinput';
import 'react-tagsinput/react-tagsinput.css';
import Dropzone from 'react-dropzone'
import axios from 'axios'
import Cookies from 'js-cookie'


const CreateProduct = (props) => {
    let product = props.product
    if (props.product == undefined) {
        product = {
            title: '',
            sku: '',
            description: '',
            product_variant_prices: [],
            product_variants: [
                {
                    option: 1,
                    tags: []
                }
            ]
        }
    } else {
        product = JSON.parse(props.product.replaceAll("'", '"'))
    }
    const [title, setTitle] = useState(product.title)
    const [sku, setSku] = useState(product.sku)
    const [description, setDescription] = useState(product.description)
    const [productVariantPrices, setProductVariantPrices] = useState(product.product_variant_prices)
    const [productVariants, setProductVariant] = useState(product.product_variants)
    const [uploadFiles, setUploadFiles] = useState([])
    // console.log(typeof props.variants)
    // handle click event of the Add button
    const handleAddClick = () => {
        let all_variants = JSON.parse(props.variants.replaceAll("'", '"')).map(el => el.id)
        let selected_variants = productVariants.map(el => el.option);
        let available_variants = all_variants.filter(entry1 => !selected_variants.some(entry2 => entry1 == entry2))
        setProductVariant([...productVariants, {
            option: available_variants[0],
            tags: []
        }])
    };

    // handle input change on tag input
    const handleInputTagOnChange = (value, index) => {
        let product_variants = [...productVariants]
        product_variants[index].tags = value
        setProductVariant(product_variants)

        checkVariant()
    }

    // remove product variant
    const removeProductVariant = (index) => {
        let product_variants = [...productVariants]
        product_variants.splice(index, 1)
        setProductVariant(product_variants)
    }

    // check the variant and render all the combination
    const checkVariant = () => {
        let tags = [];

        productVariants.filter((item) => {
            tags.push(item.tags)
        })

        setProductVariantPrices([])

        getCombn(tags).forEach(item => {
            setProductVariantPrices(productVariantPrice => [...productVariantPrice, {
                title: item,
                price: 0,
                stock: 0
            }])
        })

    }

    // combination algorithm
    function getCombn(arr, pre) {
        pre = pre || '';
        if (!arr.length) {
            return pre;
        }
        let ans = arr[0].reduce(function (ans, value) {
            return ans.concat(getCombn(arr.slice(1), pre + value + '/'));
        }, []);
        return ans;
    }

    // Save product
    let saveProduct = (event) => {
        event.preventDefault();
        let formData = new FormData();

        formData.append('title', title)
        formData.append('sku', sku)
        formData.append('description', description)

        formData.append('product_variants', JSON.stringify(productVariants))
        formData.append('product_variant_prices', JSON.stringify(productVariantPrices))
        formData.append('product_images', JSON.stringify(uploadFiles))

        const url = props.product == undefined ? '/product/create/' : '/product/edit/' + product.id + '/'

        axios.post(url, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
                'X-CSRFToken': Cookies.get('csrftoken')
            },
        }).then(response => {
            console.log(response)
        }, error => {
            console.log(error)
        }, () => {
            console.log('request completed')
        })
    }


    return (
        <div>
            <section>
                <div className="row">
                    <div className="col-md-6">
                        <div className="card shadow mb-4">
                            <div className="card-body">
                                <div className="form-group">
                                    <label htmlFor="">Product Name</label>
                                    <input value={title} onChange={(e)=> setTitle(e.target.value)} type="text" placeholder="Product Name" className="form-control"/>
                                </div>
                                <div className="form-group">
                                    <label htmlFor="">Product SKU</label>
                                    <input value={sku} onChange={(e)=> setSku(e.target.value)} type="text" placeholder="Product SKU" className="form-control"/>
                                </div>
                                <div className="form-group">
                                    <label htmlFor="">Description</label>
                                    <textarea value={description} onChange={(e)=> setDescription(e.target.value)} id="" cols="30" rows="4" className="form-control"></textarea>
                                </div>
                            </div>
                        </div>

                        <div className="card shadow mb-4">
                            <div
                                className="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                                <h6 className="m-0 font-weight-bold text-primary">Media</h6>
                            </div>
                            <div className="card-body border">
                                <Dropzone onDrop={acceptedFiles => setUploadFiles(acceptedFiles)}>
                                    {({getRootProps, getInputProps}) => (
                                        <section>
                                            <div {...getRootProps()}>
                                                <input {...getInputProps()} />
                                                <p>Drag 'n' drop some files here, or click to select files</p>
                                            </div>
                                        </section>
                                    )}
                                </Dropzone>
                            </div>
                        </div>
                    </div>

                    <div className="col-md-6">
                        <div className="card shadow mb-4">
                            <div
                                className="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                                <h6 className="m-0 font-weight-bold text-primary">Variants</h6>
                            </div>
                            <div className="card-body">

                                {
                                    productVariants.map((element, index) => {
                                        return (
                                            <div className="row" key={index}>
                                                <div className="col-md-4">
                                                    <div className="form-group">
                                                        <label htmlFor="">Option</label>
                                                        <select className="form-control" defaultValue={element.option}>
                                                            {
                                                                JSON.parse(props.variants.replaceAll("'", '"')).map((variant, index) => {
                                                                    return (<option key={index}
                                                                                    value={variant.id}>{variant.title}</option>)
                                                                })
                                                            }

                                                        </select>
                                                    </div>
                                                </div>

                                                <div className="col-md-8">
                                                    <div className="form-group">
                                                        {
                                                            productVariants.length > 1
                                                                ? <label htmlFor="" className="float-right text-primary"
                                                                         style={{marginTop: "-30px"}}
                                                                         onClick={() => removeProductVariant(index)}>remove</label>
                                                                : ''
                                                        }

                                                        <section style={{marginTop: "30px"}}>
                                                            <TagsInput value={element.tags}
                                                                       style="margin-top:30px"
                                                                       onChange={(value) => handleInputTagOnChange(value, index)}/>
                                                        </section>

                                                    </div>
                                                </div>
                                            </div>
                                        )
                                    })
                                }


                            </div>
                            <div className="card-footer">
                                {productVariants.length !== 3
                                    ? <button className="btn btn-primary" onClick={handleAddClick}>Add another
                                        option</button>
                                    : ''
                                }

                            </div>

                            <div className="card-header text-uppercase">Preview</div>
                            <div className="card-body">
                                <div className="table-responsive">
                                    <table className="table">
                                        <thead>
                                        <tr>
                                            <td>Variant</td>
                                            <td>Price</td>
                                            <td>Stock</td>
                                        </tr>
                                        </thead>
                                        <tbody>
                                        {
                                            productVariantPrices.map((productVariantPrice, index) => {
                                                const handlePriceChange = (e) => {
                                                  const updatedPrices = [...productVariantPrices];
                                                  updatedPrices[index].price = e.target.value;
                                                  setProductVariantPrices(updatedPrices);
                                                };
                                              
                                                const handleStockChange = (e) => {
                                                  const updatedPrices = [...productVariantPrices];
                                                  updatedPrices[index].stock = e.target.value;
                                                  setProductVariantPrices(updatedPrices);
                                                };
                                              
                                                return (
                                                  <tr key={index}>
                                                    <td>{productVariantPrice.title}</td>
                                                    <td>
                                                      <input
                                                        onChange={handlePriceChange}
                                                        value={productVariantPrice.price}
                                                        className="form-control"
                                                        type="text"
                                                      />
                                                    </td>
                                                    <td>
                                                      <input
                                                        onChange={handleStockChange}
                                                        value={productVariantPrice.stock}
                                                        className="form-control"
                                                        type="text"
                                                      />
                                                    </td>
                                                  </tr>
                                                );
                                              })
                                            
                                        }
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <button type="button" onClick={saveProduct} className="btn btn-lg btn-primary">Save</button>
                <button type="button" className="btn btn-secondary btn-lg">Cancel</button>
            </section>
        </div>
    );
};

export default CreateProduct;
